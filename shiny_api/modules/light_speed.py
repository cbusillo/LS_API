"""call and iterate Item class do update pricing"""
import re
import json
import datetime
from functools import lru_cache
from selenium import webdriver
from shiny_api.classes.ls_customer import Customer
from shiny_api.classes import ls_item
from shiny_api.modules.load_config import Config

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
    browser = webdriver.Safari(
        port=0, executable_path="/usr/bin/safaridriver", quiet=False
    )

    # call LS API to load all items and return a list of Item objects
    output = "Loading items"
    send_message(output)
    print(output)
    items = ls_item.Item.get_items_by_category(
        categories=Config.DEVICE_CATEGORIES_FOR_PRICE
    )
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
                    json_price = get_website_prices(
                        browser, scrape_url.format(deviceURL=device_url)
                    )

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
                output = f"{item.description} Size:{size_mult} Age:{device_age} Base:{device_base_price} Item Price: {device_price}"
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
    customers = Customer.get_all_customers()
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


if __name__ == "__main__":
    format_customer_phone()
