"""Connect to LS API and handle rate limiter"""
import os
import time
import requests
from config import secret

print(f"Importing {os.path.basename(__file__)}...")

ACCOUNT_ID = 111082  # LS account number
accessToken = secret.access_token  # imported secret info for API

ls_urls = {
    # URLS for LS API
    "access": "https://cloud.lightspeedapp.com/oauth/access_token.php",
    "item": f"https://api.lightspeedapp.com/API/V3/Account/{ACCOUNT_ID}/Item.json",
    "itemPut": f"https://api.lightspeedapp.com/API/V3/Account/{ACCOUNT_ID}/Item/{{itemID}}.json",
    "itemMatrix": f"https://api.lightspeedapp.com/API/V3/Account/{ACCOUNT_ID}/ItemMatrix.json",
    "customer": f"https://api.lightspeedapp.com/API/V3/Account/{ACCOUNT_ID}/Customer.json",
    "customerPut": f"https://api.lightspeedapp.com/API/V3/Account/{ACCOUNT_ID}/Customer/{{customerID}}.json",
}

accessHeader = {"Authorization": ""}


def generate_access():
    """Generate access requirements."""
    response = requests.post(ls_urls["access"], data=accessToken, timeout=60)
    accessHeader["Authorization"] = "Bearer " + response.json()["access_token"]


def get_data(currenturl, current_params=""):
    """Get requested data from LS API"""
    response = requests.get(currenturl, headers=accessHeader, params=current_params, timeout=60)

    while response.status_code == 429:
        print(
            f"\nDelaying for rate limit. Level:{response.headers['x-ls-api-bucket-level']} ",
            "Retry After:{response.headers['retry-after']}",
            end="\r",
        )
        time.sleep(int(response.headers["retry-after"]) + 1)
        response = requests.get(currenturl, headers=accessHeader, params=current_params, timeout=60)

    if response.status_code == 401:
        generate_access()
        response = requests.get(currenturl, headers=accessHeader, params=current_params, timeout=60)

    if response.status_code != 200:
        print(f"Received bad status code {current_params}: " + response.text)
    return response


def put_data(currenturl, current_data):
    """Put requested data into LS API"""
    response = requests.put(currenturl, headers=accessHeader, json=current_data, timeout=60)
    while response.status_code == 429:
        print(
            f"\nDelaying for rate limit. Level:{response.headers['x-ls-api-bucket-level']} ",
            "Retry After:{response.headers['retry-after']}",
            end="\r",
        )
        time.sleep(int(response.headers["retry-after"]) + 1)
        response = requests.put(currenturl, headers=accessHeader, json=current_data, timeout=60)

    if response.status_code == 401:
        generate_access()
        response = requests.put(currenturl, headers=accessHeader, json=current_data, timeout=60)

    if response.status_code != 200:
        print(f"Received bad status code on {current_data}: " + response.text)
