"""Client for Lightspeed API Inherited from requests.Session"""
import logging
import time
from dataclasses import fields, is_dataclass
from datetime import datetime
from typing import Any, Generator, Optional, Self
from urllib.parse import urljoin

import requests

from shiny_app.django_server.ls_functions.views import send_message
from shiny_app.classes.config import Config


class Client(requests.Session):
    """Client class for Lightspeed API Inherited from requests.Session"""

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

    def get_entities(self, url: str, key_name: str, params: Optional[dict] = None) -> Generator[Self, None, None]:
        """Iterate over all items in the API"""

        next_url = url
        page = 0
        while next_url != "":
            send_message(f"Getting page {page} of {key_name}")
            self._response = self.get(next_url, params=params)
            if not isinstance(self._response, requests.models.Response):
                return
            entries = self._response.json().get(key_name)
            if not entries:
                return
            if not isinstance(entries, list):
                yield entries
                return

            for entry in entries:
                yield entry

            next_url = self._response.json()["@attributes"]["next"]
            page += 1


class BaseLSEntity:
    """Base entity class for Lightspeed Objects"""

    client = Client()
    cls_params = {"limit": "100"}

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
        params.update(cls.cls_params)
        key_name = cls.__name__
        url = f"{key_name}.json"
        if entity_id:
            url = f"{key_name}/{entity_id}.json"
        if date_filter:
            params["timeStamp"] = f">,{date_filter}"
        return cls.client.get_entities(url, key_name=key_name, params=params)

    def put_entity_json(self, entity_id: int, data: dict[str, Any]) -> None:
        """Update entity"""
        url = f"{self.__class__.__name__}/{entity_id}.json"
        self.client.put(url, json=data)

    @classmethod
    def discard_extra_args(cls, *args, **kwargs) -> Self:
        """Discard extra arguments passed to the constructor for dataclasses"""
        if not is_dataclass(cls):
            raise TypeError("cls must be a dataclass")
        allowed_kwargs = {key: value for key, value in kwargs.items() if key in [field.name for field in fields(cls)]}

        return cls(**allowed_kwargs)
