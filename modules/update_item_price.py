"""call and iterate Item class do update pricing"""
import os
import json
import datetime
from selenium import webdriver
from classes import ls_item

print(f"Importing {os.path.basename(__file__)}...")


def run_update_item_price():
    """ "//device key": ["current model?", "year", "basePrice", "cellPrice", "store URL"]"""
    with open("config/devices.json", encoding="utf8") as file:
        devices = json.load(file)

    # "//max age": "price multiplier"
    with open("config/age.json", encoding="utf8") as file:
        age_price = json.load(file)

    # Apple URL to load pricing from
    scrape_url = "https://www.apple.com/shop/buy-{deviceURL}"
    browser = webdriver.Safari()

    # call LS API to load all items and return a list of Item objects
    print("Loading items")
    #label.set("Loading items")
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
                if "cell" in item.description.lower():
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
                    json_price = json.loads(json_price)

                    # Iterage through web prices and try to find match on current item.
                    # Use deviceBasePrice to subtract from new price.  Detect if cellular
                    for product in json_price["data"]["products"]:
                        if size.lower() in product["name"].lower():
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
                debug_output = (
                    "{description} Size:{sizeMult} Age:{deviceAge}"
                    + "Base:{deviceBasePrice} Item Price: {price}"
                )
                print(
                    debug_output.format(
                        description=item.description,
                        sizeMult=size_mult,
                        deviceAge=device_age,
                        deviceBasePrice=device_base_price,
                        price=device_price,
                    )
                )
                # load new price into all three LS item prices in Item object
                for item_price in item.prices.item_price:
                    if float(item_price.amount) != float(device_price):
                        item_price.amount = device_price
                        item.is_modified = True
                # Item fucntion to make API put call and save price
                if item.is_modified:
                    print(f"    Updating {item.description}")
                    ls_item.Item.save_item_price(item)
                break
