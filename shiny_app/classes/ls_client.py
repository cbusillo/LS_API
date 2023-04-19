"""Client for Lightspeed API Inherited from requests.Session"""
import logging
import json
import re
import time
from abc import abstractmethod
from dataclasses import fields, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, Optional, Self
from urllib.parse import urljoin

import pytz
import requests
from django.db import models
from django.utils import timezone  # pylint: disable=wrong-import-order

from shiny_app.classes.config import Config
from shiny_app.django_server.functions.views import send_message


class Client(requests.Session):
    """Client class for Lightspeed API Inherited from requests.Session"""

    CACHE_DIR = Config.CONFIG_SECRET_DIR / "cache"
    use_cache = False

    def __init__(self) -> None:
        super().__init__()

        def rate_hook(response_hook, *_args, **_kwargs):
            if "x-ls-api-bucket-level" in response_hook.headers:
                rate_level, rate_limit = response_hook.headers["x-ls-api-bucket-level"].split("/")
                rate_level = int(float(rate_level))
                rate_limit = int(float(rate_limit))

                logging.info("rate: %i/%i", rate_level, rate_limit)
                if rate_limit - rate_level < 10:
                    logging.warning("Rate limit reached, sleeping for 1 second")
                    send_message("Rate limit reached, sleeping for 1 second")
                    time.sleep(1)

            if response_hook.status_code == 200:
                return

            if response_hook.status_code == 429:
                retry_seconds = int(float(response_hook.headers["Retry-After"]))
                logging.info("rate limit reached, sleeping for %i", retry_seconds)
                send_message(f"Rate limit reached, sleeping for {retry_seconds}")
                time.sleep(retry_seconds)
            if response_hook.status_code == 401:
                self.auth_header = self.get_auth_header()
                self.headers.update(self.auth_header)
            logging.error("received bad status code: %s", response_hook.text)

        self.token = Config.ACCESS_TOKEN
        self.auth_url = Config.LS_URLS["access"]
        self.base_url = f"https://api.lightspeedapp.com/API/V3/Account/{Config.LS_ACCOUNT_ID}/"
        self.auth_header = self.get_auth_header()
        self.headers.update(self.auth_header)
        self._response: requests.Response
        self.hooks["response"].append(rate_hook)

    def get_auth_header(self) -> dict[str, str]:
        """get or reauthorize the auth header"""
        auth_response = requests.post(self.auth_url, data=self.token, timeout=60)
        return {"Authorization": f"Bearer {auth_response.json()['access_token']}"}

    def request(self, method: str, url: str, *args, **kwargs) -> requests.Response | None:
        """extened request method to add base url and timeouts"""
        if "://" not in url:
            url = urljoin(self.base_url, url)
        if "timeout" not in kwargs:
            kwargs["timeout"] = 10
        response_code = 0
        retries = 5
        while response_code != 200:
            request_response = super().request(method, url, *args, **kwargs)
            response_code = request_response.status_code
            retries -= 1
            if retries == 0:
                raise TimeoutError
            if response_code == 404:
                return None
        return request_response  # pyright: reportUnboundVariable=false

    def get_entities_from_api(self, url: str, key_name: str, params: Optional[dict] = None) -> Generator[Self, None, None]:
        """Iterate over all items in the API with caching"""

        def _cache_key(page: int) -> str:
            return f"{key_name}_page{page}.cache"

        def _load_from_cache(page: int) -> Optional[dict]:
            cache_file = self.CACHE_DIR / _cache_key(page)
            if not cache_file.is_file():
                return None
            with open(cache_file, "r", encoding="utf-8") as file:
                return json.load(file)

        def _save_to_cache(page: int, data: dict) -> None:
            Path.mkdir(self.CACHE_DIR, exist_ok=True, parents=True)
            cache_file = self.CACHE_DIR / _cache_key(page)
            with open(cache_file, "w", encoding="utf-8") as file:
                json.dump(data, file)

        next_url = url
        page = 0
        while next_url != "":
            send_message(f"Getting page {page} of {key_name}")
            data = None
            if self.use_cache:
                data = _load_from_cache(page)
            if data is None:
                self._response = self.get(next_url, params=params)
                if not isinstance(self._response, requests.models.Response):
                    return
                data = self._response.json().get(key_name)
                if not data or not self.use_cache:
                    return
                _save_to_cache(page, data)

            if not isinstance(data, list):
                yield data
                return

            for entry in data:
                yield entry

            next_url = self._response.json()["@attributes"]["next"]
            page += 1


class BaseLSEntityMeta(type):
    """Hold class variables for each entity class"""

    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        cls.class_params: dict[str, Any]


class BaseLSEntity(metaclass=BaseLSEntityMeta):
    """Base entity class for Lightspeed Objects"""

    client = Client()
    base_class_params = {"limit": "100", "archived": "true"}

    def __init__(self) -> None:
        self.fetch_from_api: Optional[bool] = None

    @staticmethod
    def string_to_datetime(string_input: str | None) -> datetime | None:
        """Convert date string to datetime object"""
        if string_input is None:
            return None
        return datetime.strptime(string_input, "%Y-%m-%dT%H:%M:%S%z")

    @staticmethod
    def datetime_to_string(datetime_input: datetime | None) -> str | None:
        """Convert datetime object to string"""
        if datetime_input is None:
            return None
        return datetime_input.strftime("%Y-%m-%dT%H:%M:%S%z")

    @staticmethod
    def safe_int(value: Any) -> Optional[int]:
        """Return int or None"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @classmethod
    def get_entities_json(
        cls, entity_id: Optional[int] = None, params: Optional[dict[str, Any]] = None, date_filter: Optional[datetime] = None
    ) -> Generator[Any, None, None]:
        """Get one entity"""
        if params is None:
            params = {}
            params.update(cls.class_params)
            params.update(cls.base_class_params)
        key_name = cls.__name__
        url = f"{key_name}.json"
        if entity_id:
            url = f"{key_name}/{entity_id}.json"
        if date_filter:
            params["timeStamp"] = f">,{date_filter}"
        return cls.client.get_entities_from_api(url, key_name=key_name, params=params)

    def put_entity_json(self, entity_id: int, data: dict[str, Any]) -> None:
        """Update entity"""
        url = f"{self.__class__.__name__}/{entity_id}.json"
        self.client.put(url, json=data)

    def post_entity_json(self, data: dict[str, Any]) -> int:
        """Create entity"""
        entity_name = self.__class__.__name__
        url = f"{entity_name}.json"
        response = self.client.post(url, json=data)
        entity_id = int(response.json()[entity_name][f"{entity_name.lower()}ID"])
        return entity_id

    @classmethod
    def get_entities(
        cls, date_filter: Optional[datetime] = None, categories: list[int] | int | None = None
    ) -> Generator[Self, None, None]:
        """Run API auth."""
        if categories:
            if not isinstance(categories, list):
                categories = [categories]
        else:
            categories = [0]

        for category_id in categories:
            params = {}
            if cls.base_class_params:
                params.update(cls.base_class_params)
            if cls.class_params:
                params.update(cls.class_params)
            if category_id != 0:
                params = {"categoryID": category_id}

            for entity in cls.get_entities_json(date_filter=date_filter, params=params):
                yield cls.from_json(entity)

    @classmethod
    @abstractmethod
    def from_json(cls, json: dict[str, Any]) -> Self:
        """implement in child class"""
        raise NotImplementedError("from_json must be implemented in child class")

    @classmethod
    def discard_extra_args(cls, *args, **kwargs) -> Self:
        """Discard extra arguments passed to the constructor for dataclasses"""
        if not is_dataclass(cls):
            raise TypeError("cls must be a dataclass")
        allowed_kwargs = {key: value for key, value in kwargs.items() if key in [field.name for field in fields(cls)]}

        return cls(**allowed_kwargs)

    @classmethod
    def shiny_model_from_ls(cls, model: type[models.Model], date_filter: datetime | None = None):
        """Get LS items since date_filter and iterate through them"""

        if date_filter is None:
            date_filter = cls.shiny_update_from_ls_time(model)

        ls_entities = cls.get_entities(date_filter=date_filter)

        start_time = timezone.now()

        for ls_entity in ls_entities:
            module_name = re.sub(r"(?<!^)(?=[A-Z])", "_", model.__name__).lower()
            key_args = {f"ls_{module_name}_id": getattr(ls_entity, f"{module_name}_id")}
            try:
                shiny_entity = model.objects.get(**key_args)
            except model.DoesNotExist:
                shiny_entity = model(**key_args)

            convert_function = getattr(cls, f"shiny_{module_name}_from_ls")
            shiny_entity, functions_to_execute_after = convert_function(ls_entity, shiny_entity, start_time)

            shiny_entity.save()

            logging.debug("Saved Shiny %s %s", cls.__name__, shiny_entity)

            if functions_to_execute_after:
                for function_to_execute in functions_to_execute_after:
                    function_to_execute()
                logging.debug("Saved Shiny %s's children", cls.__name__)

        send_message(f"Finished updating {cls.__name__}s")

    @classmethod
    def shiny_update_from_ls_time(cls, model: type[models.Model]):
        """Convert LS date string to datetime"""
        local_tz = pytz.timezone("America/New_York")
        default_time = datetime(2000, 1, 1, 0, 0, 0, 0, tzinfo=local_tz)
        try:
            latest_ls_update_time = model.objects.filter(update_from_ls_time__isnull=False).latest("update_from_ls_time")
        except model.DoesNotExist:
            return default_time
        if hasattr(latest_ls_update_time, "update_from_ls_time"):
            return latest_ls_update_time.update_from_ls_time  # pyright: reportGeneralTypeIssues=false
        return default_time
