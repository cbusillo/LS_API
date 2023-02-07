"""Load config values from config/config.json"""
import os
import json

print(f"Importing {os.path.basename(__file__)}...")

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
CONFIG_SECRET_DIR = os.path.expanduser("~")

with open(f"{CONFIG_DIR}/config/config.json", encoding="utf8") as file:
    config_file = json.load(file)

# load secret keys from secret.json
with open(f"{CONFIG_SECRET_DIR}/.secret.json", encoding="utf8") as file:
    secret_file = json.load(file)

PRINTER_HOST = config_file["host"]
PRINTER_PORT = config_file["port"]

LS_ACCOUNT_ID = config_file["account_id"]
LS_URLS = config_file["ls_urls"]
for urls in LS_URLS:
    LS_URLS[urls] = LS_URLS[urls].replace("{ACCOUNT_ID}", str(LS_ACCOUNT_ID))

DEVICE_CATEGORIES_FOR_PRICE = config_file["device_categories_for_price"]

accessHeader = {"Authorization": ""}

CAM_PORT = config_file["cam_port"]
CAM_WIDTH = config_file["cam_width"]
CAM_HEIGHT = config_file["cam_height"]

SICKW_URL = config_file["sickw_url"]

"""Secret section"""
DB_ACCESS = secret_file["sql_access"]
ACCESS_TOKEN = secret_file["ls_api_access"]
SICKW_API_KEY = secret_file["sickw_api_key"]
SHEETS_ACCESS = secret_file["sheets_access"]


DEBUG_CODE = True
if config_file["debug_code"].lower() == "false":
    DEBUG_CODE = False
DEBUG_LOGGING = True
if config_file["debug_logging"].lower() == "false":
    DEBUG_LOGGING = False

GOOGLE_SHEETS_SERIAL_NAME = config_file["google_sheets_serial_name"]

GOOGLE_SHEETS_SERIAL_PRINT = config_file["google_sheets_serial_print"].lower() == "true"
