"""Load config values from config/config.json"""
import os
import json

print(f"Importing {os.path.basename(__file__)}...")

with open("config/config.json", encoding="utf8") as file:
    config_values = json.load(file)

with open("config/secret.json", encoding="utf8") as file:
    ACCESS_TOKEN = json.load(file)

PRINTER_HOST = config_values["host"]
PRINTER_PORT = config_values["port"]

LS_ACCOUNT_ID = config_values["account_id"]
LS_URLS = config_values["ls_urls"]
for urls in LS_URLS:
    LS_URLS[urls] = LS_URLS[urls].replace("{ACCOUNT_ID}", str(LS_ACCOUNT_ID))

DEVICE_CATEGORIES_FOR_PRICE = config_values["device_categories_for_price"]

accessHeader = {"Authorization": ""}

CAM_PORT = config_values["cam_port"]
CAM_WIDTH = config_values["cam_width"]
CAM_HEIGHT = config_values["cam_height"]
