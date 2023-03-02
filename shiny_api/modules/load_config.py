"""Load config values from config/config.json"""
import os
import json

print(f"Importing {os.path.basename(__file__)}...")


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"
CONFIG_SECRET_DIR = os.path.expanduser("~")
COG_DIR = SCRIPT_DIR + "/modules/cogs"

with open(f"{SCRIPT_DIR}/config/config.json", encoding="utf8") as file:
    config_file = json.load(file)

# load secret keys from secret.json
with open(f"{CONFIG_SECRET_DIR}/.secret.json", encoding="utf8") as file:
    secret_file = json.load(file)

PRINTER_HOST = config_file.get("host")

LS_ACCOUNT_ID = config_file.get("account_id")
LS_URLS = config_file.get("ls_urls")
for urls in LS_URLS:
    LS_URLS[urls] = LS_URLS[urls].replace("{ACCOUNT_ID}", str(LS_ACCOUNT_ID))

DEVICE_CATEGORIES_FOR_PRICE = config_file.get("device_categories_for_price")

accessHeader = {"Authorization": ""}

CAM_PORT = config_file.get("cam_port")
CAM_WIDTH = config_file.get("cam_width")
CAM_HEIGHT = config_file.get("cam_height")

SICKW_URL = config_file.get("sickw_url")

DEBUG_CODE = True
if config_file.get("debug_code").lower() == "false":
    DEBUG_CODE = False
DEBUG_LOGGING = True
if config_file.get("debug_logging").lower() == "false":
    DEBUG_LOGGING = False

GOOGLE_SHEETS_SERIAL_NAME = config_file.get("google_sheets_serial_name")

GOOGLE_SHEETS_SERIAL_PRINT = config_file.get("google_sheets_serial_print").lower() == "true"

PC_API_URL = {
    "device": " https://clientapiv2.phonecheck.com/cloud/cloudDB/GetDeviceInfo",
    "devices": "https://clientapiv2.phonecheck.com/cloud/CloudDB/v2/GetAllDevices",
}
TRELLO_INVENTORY_BOARD = "61697cfbd3529050685f9e3a"
TRELLO_LIST_DEFAULT = "61697d01d1c4463bc0fa066c"


"""Secret section"""
DB_ACCESS = secret_file.get("sql_access")
ACCESS_TOKEN = secret_file.get("ls_api_access")
SICKW_API_KEY = secret_file.get("sickw_api_key")
DISCORD_TOKEN = secret_file.get("discord_token")
TRELLO_APIKEY = secret_file.get("trello_apiKey")
TRELLO_OAUTH_TOKEN = secret_file.get("trello_oauth_token")
OPENAI_API_KEY = secret_file.get("openai_api_key")
PHONECHECK_API_KEY = secret_file.get("phonecheck_api_key")

RESPONSE_MESSAGES = [
    "Hi {name}, we are open 11-7 Tu-Sa.",
    "Hi {name}, your {product} is finished and ready for pickup any time 11-7 Tu-Sa.  See you soon",
    "Hi {name}, your {product} is finished and ready for pickup any time 11-7 Tu-Sa.  The total is {total}.  See you soon.",
    "Hi {name}, your {product} is finished and ready for pickup any time 11-7 Tu-Sa.  There is no charge.  See you soon.",
]

STYLIZED_NAMES = [
    "Mac",
    "iMac",
    "MacBook",
    "iPhone",
    "iPad",
    "Watch",
    "Pro",
    "Air",
    "Retina",
    "HDD",
]
