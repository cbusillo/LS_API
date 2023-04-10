"""call and iterate Item class do update pricing"""
# pylint: disable=ungrouped-imports
import re
import json
import logging
import sys
from datetime import datetime
from functools import lru_cache
import pytz
from selenium import webdriver
from django.db import transaction, models  # pylint: disable=wrong-import-order
from django.utils import timezone  # pylint: disable=wrong-import-order
from shiny_api.classes.ls_customer import Customer as LSCustomer
from shiny_api.classes.ls_item import Item as LSItem
from shiny_api.modules.load_config import Config

from shiny_api.django_server.inventory.models import Item as ShinyItem
from shiny_api.django_server.customers.models import (
    Customer as ShinyCustomer,
    Phone as ShinyPhone,
    Email as ShinyEmail,
)
from shiny_api.django_server.ls_functions.views import send_message


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
    print(output)
    items = LSItem.get_items_by_category(categories=Config.DEVICE_CATEGORIES_FOR_PRICE)
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
                print(output)
                send_message(output)
                # load new price into all three LS item prices in Item object
                for item_price in item.prices.item_price:
                    if float(item_price.amount) != float(device_price):
                        item_price.amount = device_price
                        item.is_modified = True
                # Item fucntion to make API put call and save price
                if item.is_modified:
                    output = f"Updating {item.description}"
                    send_message(output)
                    print(f"    {output}")
                    item.save_item_price()
                break


def format_customer_phone():
    """Load and iterate through customers, updating formatting on phone numbers."""
    customers = LSCustomer.get_customers()
    customers_updated = 0
    print("Updating customers")
    send_message("Updating customers")
    for index, customer in enumerate(customers):
        if len(customer.contact.phones.contact_phone) == 0:
            continue
        has_mobile = False
        for each_number in customer.contact.phones.contact_phone:
            cleaned_number = re.sub(r"[^0-9x]", "", each_number.number)

            if each_number.number != cleaned_number:
                each_number.number = cleaned_number
                customer.is_modified = True
            if len(each_number.number) == 7:
                each_number.number = f"757{each_number.number}"
                customer.is_modified = True
            if len(each_number.number) == 11:
                each_number.number = each_number.number[1:]
                customer.is_modified = True
            if each_number.use_type == "Mobile":
                has_mobile = True
        if customer.is_modified or has_mobile is False:
            customers_updated += 1
            output = f"{customers_updated}: Updating Customer #{index}"
            send_message(output)
            print(output, end="\r")
            customer.update_phones()


def shiny_updated_from_ls_time(model: type[models.Model]):
    """Convert LS date string to datetime"""
    local_tz = pytz.timezone("America/New_York")
    default_time = datetime(2000, 1, 1, 0, 0, 0, 0, tzinfo=local_tz)
    try:
        latest_ls_update_time = model.objects.filter(updated_from_ls_time__isnull=False).latest("updated_from_ls_time")
    except model.DoesNotExist:
        return default_time
    if hasattr(latest_ls_update_time, "updated_from_ls_time"):
        return latest_ls_update_time.updated_from_ls_time  # pyright: reportGeneralTypeIssues=false
    else:
        return default_time


def shiny_item_from_ls(shiny_item: ShinyItem, ls_item: LSItem, start_time: datetime):
    """translation layer for LSItem to ShinyItem"""
    shiny_item.default_cost = ls_item.default_cost or None
    shiny_item.average_cost = ls_item.avg_cost or None
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
    shiny_item.updated_from_ls_time = start_time

    shiny_item.save()
    logging.debug("Shiny Item %s created/updated", shiny_item.description)


def shiny_customer_from_ls(shiny_customer: ShinyCustomer, ls_customer: LSCustomer, start_time: datetime):
    """translation layer for LSCustomer to ShinyCustomer"""
    shiny_customer.ls_customer_id = ls_customer.customer_id
    shiny_customer.first_name = ls_customer.first_name.strip()
    shiny_customer.last_name = ls_customer.last_name
    shiny_customer.title = ls_customer.title
    shiny_customer.company = ls_customer.company
    shiny_customer.update_time = start_time
    shiny_customer.updated_from_ls_time = start_time
    shiny_customer.archived = ls_customer.archived
    shiny_customer.contact_id = ls_customer.contact_id
    shiny_customer.credit_account_id = ls_customer.credit_account_id
    shiny_customer.customer_type_id = ls_customer.customer_type_id
    shiny_customer.discount_id = ls_customer.discount_id
    shiny_customer.tax_category_id = ls_customer.tax_category_id

    shiny_customer.save()

    for phone in ls_customer.contact.phones.contact_phone:
        if not ShinyPhone.objects.filter(number=phone.number, use_type=phone.use_type, customer=shiny_customer).exists():
            ShinyPhone(number=phone.number, use_type=phone.use_type, customer=shiny_customer).save()

    for email in ls_customer.contact.emails.contact_email:
        if not ShinyEmail.objects.filter(address=email.address, use_type=email.use_type, customer=shiny_customer).exists():
            ShinyEmail(address=email.address, use_type=email.use_type, customer=shiny_customer).save()

    logging.debug("Shiny customer %s created/updated", shiny_customer.full_name)


def shiny_model_from_ls(model: type[models.Model], date_filter: datetime | None = None):
    """Get LS items since date_filter and iterate through them"""
    if date_filter is None:
        date_filter = shiny_updated_from_ls_time(model)

    model_name = model.__name__
    if model_name == "Item":
        ls_entities = LSItem.get_all_items(date_filter=date_filter)
    elif model_name == "Customer":
        ls_entities = LSCustomer.get_customers(date_filter=date_filter)

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
        convert_function(shiny_entity, ls_entity, start_time)

    send_message(f"Finished updating {model_name}s")


def import_items():
    """temp function to import items from LS"""
    with transaction.atomic():
        shiny_model_from_ls(ShinyItem)


def import_customers():
    """temp function to import customers from LS"""
    with transaction.atomic():
        shiny_model_from_ls(ShinyCustomer)


def delete_all():
    """temp function to delete all items and customers from shiny db"""
    ShinyItem.objects.all().delete()
    ShinyEmail.objects.all().delete()
    ShinyPhone.objects.all().delete()
    ShinyCustomer.objects.all().delete()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    DELETE_ALL = False
    if DELETE_ALL:
        delete_all()

    import_customers()
