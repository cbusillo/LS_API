"""Connect to LS API and handle rate limiter"""
import os
import time
import logging
import requests
from kivy.uix.button import Button
from shiny_api.modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")

if config.DEBUG_LOGGING is False:
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def generate_ls_access():
    """Generate access requirements."""
    response = requests.post(config.LS_URLS["access"], data=config.ACCESS_TOKEN, timeout=60)
    if response.status_code == 200:
        config.accessHeader["Authorization"] = f'Bearer {response.json()["access_token"]}'
    else:
        print(response.text)


def get_data(currenturl, current_params="", caller: Button = None):
    """Get requested data from LS API"""
    response = requests.get(currenturl, headers=config.accessHeader, params=current_params, timeout=60)

    while response.status_code == 429:
        output = (
            f"\nDelaying for rate limit. Level:{response.headers['x-ls-api-bucket-level']} "
            + f"Retry After:{response.headers['retry-after']}"
        )
        if caller:
            caller.text = f"{caller.text.split(chr(10))[0]}\n{caller.text.split(chr(10))[1]}{output}"
        print(output, end="\r")
        time.sleep(int(response.headers["retry-after"]) + 1)
        response = requests.get(currenturl, headers=config.accessHeader, params=current_params, timeout=60)

    if response.status_code == 401:
        generate_ls_access()
        response = requests.get(currenturl, headers=config.accessHeader, params=current_params, timeout=60)

    if response.status_code != 200:
        print(f"Received bad status code {current_params}: {response.text}")
    return response


def put_data(currenturl, current_data, caller: Button = None):
    """Put requested data into LS API"""
    response = requests.put(currenturl, headers=config.accessHeader, json=current_data, timeout=60)
    while response.status_code == 429:
        output = (
            f"\nDelaying for rate limit. Level:{response.headers['x-ls-api-bucket-level']} "
            + f"Retry After:{response.headers['retry-after']}"
        )
        if caller:
            caller.text = f"{caller.text.split(chr(10))[0]}\n{caller.text.split(chr(10))[1]}{output}"
        print(output, end="\r")
        time.sleep(int(response.headers["retry-after"]) + 1)
        response = requests.put(currenturl, headers=config.accessHeader, json=current_data, timeout=60)

    if response.status_code == 401:
        generate_ls_access()
        response = requests.put(currenturl, headers=config.accessHeader, json=current_data, timeout=60)

    if response.status_code != 200:
        print(f"Received bad status code on {current_data}: {response.text}")
