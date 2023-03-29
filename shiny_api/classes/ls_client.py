"""Client for Lightspeed API Inherited from requests.Session"""
from datetime import datetime
import logging
import time
from urllib.parse import urljoin
import requests
from rich import print as pprint
from shiny_api.views.ls_functions import send_message

import shiny_api.modules.load_config as config


def string_to_datetime(date_string: str) -> datetime:
    """Convert date string to datetime object"""
    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S%z")


def datetime_to_string(date_string: datetime) -> str:
    """Convert datetime object to string"""
    return date_string.strftime("%Y-%m-%dT%H:%M:%S%z")


class Client(requests.Session):
    """Client class for Lightspeed API Inherited from requests.Session"""

    def __init__(self) -> None:
        super().__init__()

        def get_auth_header() -> dict[str, str]:
            auth_response = requests.post(self.auth_url, data=self.token, timeout=60)
            return {"Authorization": f"Bearer {auth_response.json()['access_token']}"}

        def rate_hook(response_hook, *_args, **_kwargs):
            if 'x-ls-api-bucket-level' in response_hook.headers:
                rate_level, rate_limit = response_hook.headers['x-ls-api-bucket-level'].split('/')
                rate_level = int(float(rate_level))
                rate_limit = int(float(rate_limit))

                logging.info("rate: %i/%i", rate_level, rate_limit)
                if rate_limit-rate_level < 10:
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
                self.auth_header = get_auth_header()
            logging.error("received bad status code: %s", response_hook.text)

        self.token = config.ACCESS_TOKEN
        self.auth_url = config.LS_URLS["access"]
        self.base_url = f"https://api.lightspeedapp.com/API/V3/Account/{config.LS_ACCOUNT_ID}/"
        self.auth_header = get_auth_header()
        self.headers.update(self.auth_header)
        self._response = None
        self.hooks["response"].append(rate_hook)

    def request(self, method: str, url: str, *args, **kwargs) -> requests.Response:
        """extened request method to add base url and timeouts"""
        if "://" not in url:
            url = urljoin(self.base_url, url)
        response_code = 0
        retries = 5
        while response_code != 200:
            request_response = super().request(method, url, *args, **kwargs)
            response_code = request_response.status_code
            retries -= 1
            if retries == 0:
                raise TimeoutError
        return request_response  # pyright: reportUnboundVariable=false

    def _entries(self, url: str, key_name: str, params: dict | None = None):
        """Iterate over all items in the API"""

        next_url = url
        page = 0
        while next_url != "":
            send_message(f"Getting page {page}")
            self._response = self.get(next_url, params=params)
            entries = self._response.json().get(key_name)
            if isinstance(entries, dict):
                yield entries
                return

            if entries is None:
                return

            for line in entries:
                yield line
            next_url = self._response.json()["@attributes"]["next"]
            page += 1

    def _entry(self, url: str, key_name: str, params: dict | None = None):
        """Get single item from API"""
        self._response = self.get(url, params=params)
        return self._response.json().get(key_name)

    def get_items_json(self, category_id: str = "", description: str = "", date_filter: datetime | None = None):
        """Get all items"""
        params = {"load_relations": '["ItemAttributes"]', "limit": "100"}
        if date_filter:
            params["timeStamp"] = f">,{date_filter}"

        if category_id:
            params["categoryID"] = category_id
        if description:
            params["or"] = description

        return self._entries(config.LS_URLS["items"], "Item", params=params)

    def get_customers_json(self):
        """Get all items"""
        return self._entries(config.LS_URLS["customers"], "Customer", params={"load_relations": '["Contact"]', "limit": "100"})

    def get_customer_json(self, customer_id: int):
        """Get customer"""
        url = config.LS_URLS['customer'].format(customerID=customer_id)
        params = {"load_relations": '["Contact"]'}
        return self._entry(url, key_name="Customer", params=params)

    def get_workorder_json(self, workorder_id: int):
        """Get workorder"""
        url = config.LS_URLS['workorder'].format(workorderID=workorder_id)
        return self._entry(url, key_name="Workorder")

    def get_item_json(self, item_id: int):
        """Get item"""
        url = config.LS_URLS['item'].format(itemID=item_id)
        params = {"load_relations": '["ItemAttributes"]'}
        return self._entry(url, key_name="Item", params=params)

    def get_size_attributes_json(self):
        """Get all size attributes"""
        url = config.LS_URLS["itemMatrix"]
        return self._entries(url, "ItemMatrix", params={"load_relations": '["ItemAttributeSet"]'})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = Client()
    for index, item in enumerate(client.get_items_json()):
        pprint(f"Count:{index} ID:{item['itemID']} ")
    # response = client.get_item_json("19")
    # pprint(response.json())
