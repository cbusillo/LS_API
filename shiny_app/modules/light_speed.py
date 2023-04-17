"""call and iterate Item class do update pricing"""
# pylint: disable=ungrouped-imports, wrong-import-position
import os
import json
import logging
import sys
import time
from datetime import datetime
from functools import lru_cache
from urllib.parse import urlparse, parse_qs
import pytz
from seleniumbase import Driver
from selenium import webdriver
from selenium.common.exceptions import JavascriptException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from django.core.exceptions import ValidationError
from django.db import transaction, models  # pylint: disable=wrong-import-order
from django.utils import timezone  # pylint: disable=wrong-import-order

from shiny_app.classes.config import Config
from shiny_app.classes.ls_item import Item as LSItem
from shiny_app.classes.ls_workorder import Workorder as LSWorkorder
from shiny_app.classes.ls_customer import Customer as LSCustomer

from shiny_app.django_server.inventory.models import Item as ShinyItem
from shiny_app.django_server.customers.models import (
    Customer as ShinyCustomer,
    Phone as ShinyPhone,
    Email as ShinyEmail,
)
from shiny_app.django_server.workorders.models import Workorder as ShinyWorkorder
from shiny_app.django_server.ls_functions.views import send_message

driver = None
if os.environ.get("RUN_MAIN", None) == "true":
    os.system("killall -u cbusillo 'Google Chrome'")
    driver = Driver(headless2=False, uc=True)


@lru_cache
def get_website_prices(browser: webdriver.Safari, url: str):
    """decode Apple website price data and return json"""
    browser.get(url)
    price = browser.find_element("id", "metrics")
    json_price = price.text.replace("//", "")
    browser.minimize_window()
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
    time.sleep(0.5)

    driver.execute_script(f"window.merchantos.quick_customer.attachCustomer({customer_id})")
    wait.until(lambda driver: "&id=undefined&" not in driver.current_url)
    workorder_ids = parse_qs(urlparse(driver.current_url).query).get("id")
    workorder_id = None
    if workorder_ids:
        workorder_id = workorder_ids[0]
    return workorder_id


def update_item_price():
    """ "//device key": ["current model?", "year", "basePrice", "cellPrice", "store URL"]"""

    with open(f"{Config.SCRIPT_DIR}/config/devices.json", encoding="utf8") as file:
        devices = json.load(file)

    # "//max age": "price multiplier"
    with open(f"{Config.SCRIPT_DIR}/config/age.json", encoding="utf8") as file:
        age_price = json.load(file)

    # Apple URL to load pricing from
    scrape_url = "https://www.apple.com/shop/buy-{deviceURL}"
    browser = webdriver.Safari(port=0, executable_path="/usr/bin/safaridriver", quiet=False)

    # call LS API to load all items and return a list of Item objects
    output = "Loading items"
    send_message(output)
    logging.info(output)
    items = LSItem.get_items(categories=Config.DEVICE_CATEGORIES_FOR_PRICE)
    for item in items:
        # interate through items to generate pricing and save to LS
        # Generate pricing from devices.json and apple website by item from LS
        # check to see where current item's storage falls numerically in matrix
        size = ""
        size_mult = 0
        for size_mult, size in enumerate(item.sizes):
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
                if "cell" in item.description.lower() and device_cell_price > 0:
                    device_base_price = device_cell_price
                # use device.json age to calculate from current
                # and look for that age multiplier in age.json
                device_age = datetime.date.today().year - device_year
                age_mult = 0
                for age, price in age_price.items():
                    if device_age < int(age):
                        age_mult = price
                        break
                # if device is currently sold (documented in ages.json),
                # load json from Apple web store and find price. Use URL key from devices.json
                if device_current:
                    json_price = get_website_prices(browser, scrape_url.format(deviceURL=device_url))

                    # Iterage through web prices and try to find match on current item.
                    # Use deviceBasePrice to subtract from new price.  Detect if cellular
                    apple_price = 0
                    for product in json_price["data"]["products"]:
                        if size.lower() not in product["name"].lower():
                            continue
                        if "12.9" in device_name and "12.9" not in product["name"]:
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


def shiny_update_from_ls_time(model: type[models.Model]):
    """Convert LS date string to datetime"""
    local_tz = pytz.timezone("America/New_York")
    default_time = datetime(2000, 1, 1, 0, 0, 0, 0, tzinfo=local_tz)
    try:
        latest_ls_update_time = model.objects.filter(update_from_ls_time__isnull=False).latest("update_from_ls_time")
    except model.DoesNotExist:
        return default_time
    if hasattr(latest_ls_update_time, "update_from_ls_time"):
        return latest_ls_update_time.update_from_ls_time  # pyright: reportGeneralTypeIssues=false
    return default_time


def shiny_workorder_from_ls(shiny_workorder: ShinyWorkorder, ls_workorder: LSWorkorder, start_time: datetime):
    """Convert LS Workorder to Shiny Workorder"""
    shiny_workorder.ls_workorder_id = ls_workorder.workorder_id
    shiny_workorder.time_in = ls_workorder.time_in
    shiny_workorder.eta_out = ls_workorder.eta_out
    shiny_workorder.note = ls_workorder.note
    shiny_workorder.warranty = ls_workorder.warranty
    shiny_workorder.tax = ls_workorder.tax
    shiny_workorder.archived = ls_workorder.archived
    shiny_workorder.update_time = start_time
    shiny_workorder.update_from_ls_time = start_time
    # shiny_workorder.total = ls_workorder.total
    shiny_workorder.item_description = ls_workorder.item_description
    shiny_workorder.status = ls_workorder.status
    try:
        shiny_workorder.customer = ShinyCustomer.objects.get(ls_customer_id=ls_workorder.customer_id)
    except ShinyCustomer.DoesNotExist:
        shiny_workorder.customer = ShinyCustomer.objects.get(ls_customer_id=5896)

    return shiny_workorder, None


def shiny_item_from_ls(shiny_item: ShinyItem, ls_item: LSItem, start_time: datetime):
    """translation layer for LSItem to ShinyItem"""
    shiny_item.ls_item_id = ls_item.item_id
    shiny_item.default_cost = ls_item.default_cost or None
    shiny_item.average_cost = ls_item.average_cost or None
    shiny_item.tax = ls_item.tax
    shiny_item.archived = ls_item.archived
    shiny_item.item_type = ls_item.item_type
    shiny_item.serialized = ls_item.serialized
    shiny_item.description = ls_item.description.strip().replace("  ", " ")
    shiny_item.upc = ls_item.upc
    shiny_item.custom_sku = ls_item.custom_sku
    shiny_item.manufacturer_sku = ls_item.manufacturer_sku
    shiny_item.item_matrix_id = ls_item.item_matrix_id
    shiny_item.item_attributes = None
    shiny_item.update_time = start_time
    shiny_item.update_from_ls_time = start_time

    return shiny_item, None


def shiny_customer_from_ls(shiny_customer: ShinyCustomer, ls_customer: LSCustomer, start_time: datetime):
    """translation layer for LSCustomer to ShinyCustomer"""
    shiny_customer.ls_customer_id = ls_customer.customer_id
    shiny_customer.first_name = ls_customer.first_name
    shiny_customer.last_name = ls_customer.last_name
    shiny_customer.title = ls_customer.title
    shiny_customer.company = ls_customer.company
    shiny_customer.update_time = start_time
    shiny_customer.update_from_ls_time = start_time
    shiny_customer.archived = ls_customer.archived
    shiny_customer.contact_id = ls_customer.contact_id
    shiny_customer.credit_account_id = ls_customer.credit_account_id
    shiny_customer.customer_type_id = ls_customer.customer_type_id
    shiny_customer.tax_category_id = ls_customer.tax_category_id
    functions_to_execute_after = []

    for phone in ls_customer.phones:
        if not ShinyPhone.objects.filter(number=phone.number, number_type=phone.number_type, customer=shiny_customer).exists():
            functions_to_execute_after.append(
                ShinyPhone(number=phone.number, number_type=phone.number_type, customer=shiny_customer).save
            )

    for email in ls_customer.emails:
        if not ShinyEmail.objects.filter(address=email.address, address_type=email.address_type, customer=shiny_customer).exists():
            functions_to_execute_after.append(
                ShinyEmail(address=email.address, address_type=email.address_type, customer=shiny_customer).save
            )

    return shiny_customer, functions_to_execute_after


def _shiny_model_from_ls(model: type[models.Model], date_filter: datetime | None = None):
    """Get LS items since date_filter and iterate through them"""
    if date_filter is None:
        date_filter = shiny_update_from_ls_time(model)

    model_name = model.__name__
    if model_name == "Item":
        ls_entities = LSItem.get_items(date_filter=date_filter)
    elif model_name == "Customer":
        ls_entities = LSCustomer.get_customers(date_filter=date_filter)
    elif model_name == "Workorder":
        ls_entities = LSWorkorder.get_workorders(date_filter=date_filter)
    else:
        logging.warning("Invalid model type passed to shiny_model_from_ls")
        return

    start_time = timezone.now()

    for ls_entity in ls_entities:
        module_name = f"{model.__name__.lower()}"
        key_args = {f"ls_{module_name}_id": getattr(ls_entity, f"{module_name}_id")}
        try:
            shiny_entity = model.objects.get(**key_args)
        except model.DoesNotExist:
            shiny_entity = model(**key_args)

        convert_function = getattr(sys.modules[__name__], f"shiny_{module_name}_from_ls")
        shiny_entity, functions_to_execute_after = convert_function(shiny_entity, ls_entity, start_time)

        try:
            shiny_entity.save()
        except ValidationError as error:
            logging.error("Error saving Shiny %s %s", model_name, error)

        logging.debug("Saved Shiny %s %s", model_name, shiny_entity)

        if functions_to_execute_after:
            for function_to_execute in functions_to_execute_after:
                try:
                    function_to_execute()
                except ValidationError as error:
                    logging.error("Error saving Shiny %s %s", model_name, error)
            logging.debug("Saved Shiny %s's children", model_name)

    send_message(f"Finished updating {model_name}s")


def import_items():
    """temp function to import items from LS"""
    with transaction.atomic():
        _shiny_model_from_ls(ShinyItem)


def import_customers():
    """temp function to import customers from LS"""
    with transaction.atomic():
        _shiny_model_from_ls(ShinyCustomer)


def import_workorders():
    """temp function to import workorders from LS"""
    import_customers()
    with transaction.atomic():
        _shiny_model_from_ls(ShinyWorkorder)


def import_all():
    """Import everything from LS, use to create db"""
    import_items()
    import_customers()
    import_workorders()


def delete_all():
    """temp function to delete all items and customers from shiny db"""
    ShinyWorkorder.objects.all().delete()
    ShinyItem.objects.all().delete()
    ShinyEmail.objects.all().delete()
    ShinyPhone.objects.all().delete()
    ShinyCustomer.objects.all().delete()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    DELETE_ALL = False
    if DELETE_ALL:
        delete_all()

    # import_all()
    test_customer = LSCustomer()
    test_customer.first_name = "test"
    test_customer.last_name = "test"
    test_customer.phones = LSCustomer.Phone(**{"number": "1234566789", "number_type": "mobile"})
    test_customer.emails = LSCustomer.Email(**{"address": "test@test.com", "address_type": "Primary"})

    print(test_customer)
