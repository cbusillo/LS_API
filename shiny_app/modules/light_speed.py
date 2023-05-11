"""call and iterate Item class do update pricing"""
# pylint: disable=ungrouped-imports, wrong-import-position
import os
import json
import logging
import time
import platform
from typing import Optional
from pathlib import Path
from datetime import datetime
from functools import lru_cache
from urllib.parse import urlparse, parse_qs
from seleniumbase import Driver
from selenium.common.exceptions import JavascriptException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from django.db import transaction, models
from django.apps import apps
from shiny_app.classes.config import Config
from shiny_app.classes.ls_client import Client
from shiny_app.classes.ls_item import Item as LSItem
from shiny_app.classes.ls_workorder import (
    Workorder as LSWorkorder,
    WorkorderItem as LSWorkorderItem,
    WorkorderLine as LSWorkorderLine,
)
from shiny_app.classes.ls_customer import Customer as LSCustomer
from shiny_app.classes.ls_serial import Serialized as LSSerial
from shiny_app.classes.ls_sale import Sale as LSSale, SaleLine as LSSaleLine

from shiny_app.django_apps.items.models import Item as ShinyItem, Serial as ShinySerial

from shiny_app.django_apps.customers.models import Customer as ShinyCustomer

from shiny_app.django_apps.workorders.models import (
    Workorder as ShinyWorkorder,
    WorkorderItem as ShinyWorkorderItem,
    WorkorderLine as ShinyWorkorderLine,
)


from shiny_app.django_apps.sales.models import Sale as ShinySale, SaleLine as ShinySaleLine

from shiny_app.django_apps.functions.views import send_message

driver = None
if os.environ.get("RUN_MAIN", None) == "true":
    os.system("killall -u cbusillo 'Google Chrome'")
    if "imagingserver" in platform.node().lower():
        driver = Driver(headless=True, uc=True)
    else:
        driver = Driver(headless=True, uc=True)


@lru_cache
def get_website_prices(driver: WebDriver, url: str):
    """decode Apple website price data and return json"""
    driver.get(url)
    price = driver.find_element(By.ID, "metrics")
    json_price = price.get_attribute("innerHTML").replace("//", "")
    json_price = json_price.split("[[")[0] + "}}"
    json_price = json_price.replace(',"sectionEngagement":', "")
    json_price = json_price.replace('"}]}}}}', '"}]}}')
    json_price = json_price.replace('"shop"}}}}', '"shop"}}')
    json_price = json_price.replace('{"step":"select"}}}}}', '{"step":"select"}}}')
    return json.loads(json_price)


class JsFunctionAvailable:
    """check if a javascript function is available"""

    def __init__(self, function_name):
        self.function_name = function_name

    def __call__(self, driver):
        try:
            return driver.execute_script(f"return typeof window.{self.function_name} === 'function';")
        except JavascriptException:
            return False


def element_to_be_clickable_by_css_selector(css_selector: str):
    """check if an element is ready to be clicked"""

    def element_to_be_clickable(driver) -> WebElement | None:
        element = driver.find_element(By.CSS_SELECTOR, css_selector)
        if element.is_enabled():
            return element
        return None

    return element_to_be_clickable


def create_workorder(customer_id: int) -> int | None:
    """Create a workorder in LS using Selenium"""
    if driver is None:
        return None
    driver.get("https://us.merchantos.com/?name=workbench.views.beta_workorder&form_name=view&id=undefined&tab=details")
    wait = WebDriverWait(driver, 10)
    if "/login?" in driver.current_url:
        login_field = wait.until(EC.visibility_of_element_located((By.ID, "login-input")))
        password_field = wait.until(EC.visibility_of_element_located((By.ID, "password-input")))
        login_button = wait.until(element_to_be_clickable_by_css_selector(".vd-btn.vd-btn--do"))

        login_field.send_keys(Config.LS_LOGIN_EMAIL)
        password_field.send_keys(Config.LS_LOGIN_PASSWORD)

        login_button.click()
    wait.until(JsFunctionAvailable("merchantos.quick_customer.attachCustomer"))
    time.sleep(1.5)

    driver.execute_script(f"window.merchantos.quick_customer.attachCustomer({customer_id})")
    wait.until(lambda driver: "&id=undefined&" not in driver.current_url)
    workorder_ids = parse_qs(urlparse(driver.current_url).query).get("id")
    workorder_id = None
    if workorder_ids:
        workorder_id = workorder_ids[0]
    return workorder_id


def update_item_price():
    """ "//device key": ["current model?", "year", "basePrice", "cellPrice", "store URL"]"""

    with open(f"{Config.SCRIPT_DIR}/config/devices.json", encoding="utf8", mode="r") as file:
        devices = json.load(file)

    # "//max age": "price multiplier"
    with open(f"{Config.SCRIPT_DIR}/config/age.json", encoding="utf8", mode="r") as file:
        age_price = json.load(file)

    # Apple URL to load pricing from
    scrape_url = "https://www.apple.com/shop/buy-{deviceURL}"

    # call LS API to load all items and return a list of Item objects
    output = "Loading items"
    send_message(output)
    logging.info(output)
    items = LSItem.get_entities(categories=Config.DEVICE_CATEGORIES_FOR_PRICE)
    for item in items:
        if "iPhone 12 Pro" in item.description:
            pass
        # interate through items to generate pricing and save to LS
        # Generate pricing from devices.json and apple website by item from LS
        # check to see where current item's storage falls numerically in matrix
        size = ""
        size_mult = 0
        if item.sizes:
            sizes = item.sizes.split("|")
            for size_mult, size in enumerate(sizes):
                if size.lower() in item.description.lower():
                    break

        for device_name, [
            device_current,
            device_year,
            device_base_price,
            device_cell_price,
            device_url,
        ] in devices.items():
            # iterate through devices.json look for matching name look for base price or cell price
            if device_name in item.description:
                apple_price = 0
                if "cell" in item.description.lower() and device_cell_price > 0:
                    device_base_price = device_cell_price
                # use device.json age to calculate from current
                # and look for that age multiplier in age.json
                device_age = datetime.today().year - device_year
                age_mult = 0
                for age, price in age_price.items():
                    if device_age < int(age):
                        age_mult = price
                        break
                # if device is currently sold (documented in ages.json),
                # load json from Apple web store and find price. Use URL key from devices.json
                if device_current:
                    json_price = get_website_prices(driver, scrape_url.format(deviceURL=device_url))

                    # Iterage through web prices and try to find match on current item.
                    # Use deviceBasePrice to subtract from new price.  Detect if cellular

                    for product in json_price["data"]["products"]:
                        if size.lower() not in product["name"].lower():
                            continue
                        if "12.9" in device_name and "12.9" not in product["name"]:
                            continue
                        if "mini" in product["name"] and "mini" not in device_name:
                            continue

                        if "cell" in item.description.lower():
                            if "cell" in product["name"].lower():
                                apple_price = product["price"]["fullPrice"]
                                break
                        else:
                            apple_price = product["price"]["fullPrice"]
                            break
                    device_price = apple_price - device_base_price
                # device isn't new, dont use web lookup and
                # generate price from base price, side and age multipliers
                else:
                    device_price = device_base_price + (size_mult * age_mult)
                output = (
                    f"{item.description} Size:{size_mult} Age:{device_age}" f" Base:{device_base_price} Item Price: {device_price}"
                )
                if device_current:
                    output += f" Apple Price: {apple_price}"
                logging.info(output)
                send_message(output)
                # load new price into all three LS item prices in Item object

                if item.price != device_price:
                    item.price = device_price
                    item.is_modified = True
                # Item fucntion to make API put call and save price
                if item.is_modified:
                    output = f"Updating {item.description}"
                    send_message(output)
                    logging.info(output)
                    item.update_item_price()
                break


def import_items():
    """temp function to import items from LS"""
    LSItem.ItemMatrix.check_size_attributes()
    with transaction.atomic():
        LSItem.shiny_model_from_ls(ShinyItem)


def import_customers():
    """temp function to import customers from LS"""
    with transaction.atomic():
        LSCustomer.shiny_model_from_ls(ShinyCustomer)
        LSSerial.shiny_model_from_ls(ShinySerial)


def import_workorders():
    """temp function to import workorders from LS"""
    with transaction.atomic():
        LSWorkorder.shiny_model_from_ls(ShinyWorkorder)
        LSWorkorderLine.shiny_model_from_ls(ShinyWorkorderLine)
        LSWorkorderItem.shiny_model_from_ls(ShinyWorkorderItem)


def import_sales():
    """temp function to import sales from LS"""
    with transaction.atomic():
        LSSale.shiny_model_from_ls(ShinySale)
        LSSaleLine.shiny_model_from_ls(ShinySaleLine)


def import_all():
    """Import everything from LS, use to create db"""
    import_items()
    import_customers()
    import_workorders()
    import_sales()


def delete_all(delete_cache: Optional[bool] = False):
    """temp function to delete all items and customers from shiny db"""
    # call_command("flush", "--noinput", interactive=False)
    for _ in range(10):
        flush_without_auth()
    if delete_cache:
        for file in Path(Config.CONFIG_SECRET_DIR / "cache").iterdir():
            file.unlink()

    Client.use_cache = True
    if not (Config.CONFIG_SECRET_DIR / "cache").exists():
        (Config.CONFIG_SECRET_DIR / "cache").mkdir(parents=True, exist_ok=True)
        with open(Config.CONFIG_SECRET_DIR / "cache" / "update_time", "w", encoding="utf-8") as file:
            file.write(datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"))

    import_all()
    Client.use_cache = False
    import_all()


def flush_without_auth():
    """Flush the database without deleting the auth models"""
    app_models = apps.get_models()

    filtered_models = [model for model in app_models if model._meta.app_label != "auth"]

    for model in filtered_models:
        try:
            model.objects.all().delete()
        except models.deletion.ProtectedError:
            print("trying to delete protected model")
