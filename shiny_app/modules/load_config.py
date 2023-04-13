"""Load config values from config/config.json"""
# pylint: disable=line-too-long
import json
from pathlib import Path


class Config:
    """class to hold config values"""

    CERTIFICATE_SERVER_HOSTNAME = "imagingserver.local"
    CERTIFICATE_SERVER_FILE = "/etc/letsencrypt/live/shinyapi.logi.wiki/"
    SCRIPT_DIR = Path(__file__).resolve().parent.parent
    CONFIG_SECRET_DIR = Path.home() / ".shiny"
    COG_DIR = SCRIPT_DIR / "discord_cogs"

    with open(f"{SCRIPT_DIR}/config/config.json", encoding="utf8") as file:
        config_file = json.load(file)

    # load secret keys from secret.json
    with open(f"{CONFIG_SECRET_DIR}/secret.json", encoding="utf8") as file:
        secret_file = json.load(file)

    FRONT_PRINTER_IP = config_file.get("front_printer_ip")
    BACK_PRINTER_IP = config_file.get("back_printer_ip")

    LS_ACCOUNT_ID = config_file.get("ls_account_id")
    LS_URLS = config_file.get("ls_urls")
    for urls in LS_URLS:
        LS_URLS[urls] = LS_URLS[urls].replace("{ACCOUNT_ID}", str(LS_ACCOUNT_ID))

    DEVICE_CATEGORIES_FOR_PRICE = config_file.get("device_categories_for_price")

    accessHeader = {"Authorization": ""}

    CAM_PORT = config_file.get("cam_port")
    CAM_WIDTH = config_file.get("cam_width")
    CAM_HEIGHT = config_file.get("cam_height")

    SICKW_URL = config_file.get("sickw_url")

    if config_file.get("debug_code").lower() == "false":
        DEBUG_CODE = False
    else:
        DEBUG_CODE = True

    if config_file.get("debug_logging").lower() == "false":
        DEBUG_LOGGING = False
    else:
        DEBUG_LOGGING = True

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
    DJANGO_SECRET_KEY = secret_file.get("django_secret_key")
    LS_LOGIN_EMAIL = secret_file.get("ls_login_email")
    LS_LOGIN_PASSWORD = secret_file.get("ls_login_password")

    HOMEASSISTANT_API = {
        store_key: {config_key: config_value for config_key, config_value in store_value.items()}
        for store_key, store_value in secret_file.get("homeassistant_api").items()
    }

    RESPONSE_MESSAGES = [
        "Hi {name}, we are open 11-7 Tu-Sa.",
        "Hi {name}, your {product} is ready for pickup any time 11-7 Tu-Sa.  See you soon.",
        "Hi {name}, your {product} is ready for pickup any time 11-7 Tu-Sa.  The total is {total}.  See you soon.",
        "Hi {name}, your {product} is ready for pickup any time 11-7 Tu-Sa.  There is no charge.  See you soon.",
        "Hi {name}, do you mind sending your password so we can complete the repair?",
        "Hi {name}, ",
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

    DEFAULT_LABELS = {
        "Main Labels": {
            "printer_ip": FRONT_PRINTER_IP,
            "labels": [
                "Fully Functional",
                "Good",
                "Bad",
                "SSD Fan Control",
                "RMA",
                "MS RMA",
                "IG RMA",
                "PT RMA",
                "Grade C",
                "Grade D",
                "Grade F",
                "Part out",
                "Bench Use",
                "app.shinycomputers.com",
                "TBT",
                "Donated",
                "Customer",
                "eBay",
            ],
        },
        "Rob's Labels": {
            "printer_ip": BACK_PRINTER_IP,
            "labels": [
                "Scrap NOT Wiped",
                "Scrap Wiped",
                "List on eBay",
                "Fully Functional",
                "Good",
                "Bad",
                "RMA",
                "MS RMA",
                "IG RMA",
                "PT RMA",
                "Grade C",
                "Grade D",
                "Grade F",
                "Part out",
                "TBT",
                "Donated",
                "eBay",
            ],
        },
        "Chris's Labels": {
            "printer_ip": FRONT_PRINTER_IP,
            "labels": ["test1", "test2", "test3"],
        },
    }
