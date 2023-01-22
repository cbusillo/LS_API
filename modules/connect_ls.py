"""Connect to LS API and handle rate limiter"""
import os
import time
import requests
from modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")


def generate_ls_access():
    """Generate access requirements."""
    response = requests.post(config.LS_URLS["access"], data=config.ACCESS_TOKEN, timeout=60)
    config.accessHeader["Authorization"] = "Bearer " + response.json()["access_token"]


def get_data(currenturl, current_params=""):
    """Get requested data from LS API"""
    response = requests.get(currenturl, headers=config.accessHeader, params=current_params, timeout=60)

    while response.status_code == 429:
        print(
            f"\nDelaying for rate limit. Level:{response.headers['x-ls-api-bucket-level']} ",
            "Retry After:{response.headers['retry-after']}",
            end="\r",
        )
        time.sleep(int(response.headers["retry-after"]) + 1)
        response = requests.get(currenturl, headers=config.accessHeader, params=current_params, timeout=60)

    if response.status_code == 401:
        generate_ls_access()
        response = requests.get(currenturl, headers=config.accessHeader, params=current_params, timeout=60)

    if response.status_code != 200:
        print(f"Received bad status code {current_params}: " + response.text)
    return response


def put_data(currenturl, current_data):
    """Put requested data into LS API"""
    response = requests.put(currenturl, headers=config.accessHeader, json=current_data, timeout=60)
    while response.status_code == 429:
        print(
            f"\nDelaying for rate limit. Level:{response.headers['x-ls-api-bucket-level']} ",
            "Retry After:{response.headers['retry-after']}",
            end="\r",
        )
        time.sleep(int(response.headers["retry-after"]) + 1)
        response = requests.put(currenturl, headers=config.accessHeader, json=current_data, timeout=60)

    if response.status_code == 401:
        generate_ls_access()
        response = requests.put(currenturl, headers=config.accessHeader, json=current_data, timeout=60)

    if response.status_code != 200:
        print(f"Received bad status code on {current_data}: " + response.text)
