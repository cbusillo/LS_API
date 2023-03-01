"""call and iterate Item class do update pricing"""
import os
import json
import datetime
from kivy.uix.button import Button
from selenium import webdriver
from shiny_api.classes import ls_item
from shiny_api.modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")


def run_update_item_price(caller: Button):
    """ "//device key": ["current model?", "year", "basePrice", "cellPrice", "store URL"]"""

    with open(f"{config.SCRIPT_DIR}/config/devices.json", encoding="utf8") as file:
        devices = json.load(file)

    # "//max age": "price multiplier"
    with open(f"{config.SCRIPT_DIR}/config/age.json", encoding="utf8") as file:
        age_price = json.load(file)

    # Apple URL to load pricing from
    scrape_url = "https://www.apple.com/shop/buy-{deviceURL}"
    browser = webdriver.Safari(port=0, executable_path="/usr/bin/safaridriver", quiet=False)

    # call LS API to load all items and return a list of Item objects
    output = "Loading items"
    caller.text = f"{caller.text.split(chr(10))[0]}\n{output}"
    print(output)
    # label.set("Loading items")
    items = ls_item.Item.get_items()
    for item in items:
        # interate through items to generate pricing and save to LS
        # Generate pricing from devices.json and apple website by item from LS
        # check to see where current item's storage falls numerically in matrix
        size = 0
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
                for age, price in age_price.items():
                    if device_age < int(age):
                        age_mult = price
                        break
                # if device is currently sold (documented in ages.json),
                # load json from Apple web store and find price. Use URL key from devices.json
                if device_current:
                    browser.get(scrape_url.format(deviceURL=device_url))
                    price = browser.find_element("id", "metrics")
                    json_price = price.text.replace("//", "")
                    browser.minimize_window()
                    json_price = json_price.split("[[")
                    json_price = json_price[0] + "}}"
                    json_price = json_price.replace(',"sectionEngagement":', "")
                    json_price = json_price.replace('"}]}}}}', '"}]}}')
                    json_price = json_price.replace('"shop"}}}}', '"shop"}}')
                    json_price = json_price.replace('{"step":"select"}}}}}', '{"step":"select"}}}')
                    json_price = json.loads(json_price)

                    # Iterage through web prices and try to find match on current item.
                    # Use deviceBasePrice to subtract from new price.  Detect if cellular
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
                caller.text = f"{caller.text.split(chr(10))[0]}\n{output}"
                print(output)
                # load new price into all three LS item prices in Item object
                for item_price in item.prices.item_price:
                    if float(item_price.amount) != float(device_price):
                        item_price.amount = device_price
                        item.is_modified = True
                # Item fucntion to make API put call and save price
                if item.is_modified:
                    output = f"Updating {item.description}"
                    caller.text = f"{caller.text.split(chr(10))[0]}\n{output}"
                    print(f"    {output}")
                    ls_item.Item.save_item_price(item)
                break
    caller.disabled = False
    caller.text = caller.text.split("\n")[0]
