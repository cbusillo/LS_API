import json
import datetime
from selenium import webdriver
import tkinter as tk

import modules.classItem as classItem

def runUpdateItemPrice():
    #"//device key": ["current model?", "year", "basePrice", "cellPrice", "store URL"]
    with open('config/devices.json') as file:
        devices = json.load(file)

    #"//max age": "price multiplier"
    with open('config/age.json') as file:
        agePrice = json.load(file)

    #Apple URL to load pricing from
    scrapeURL = 'https://www.apple.com/shop/buy-{deviceURL}'
    browser = webdriver.Safari()

    #call LS API to load all items and return a list of Item objects
    print("Loading items")
    items = classItem.Item.get_items()
    for item in items:
        #interate through items to generate pricing and save to LS
            #Generate pricing from devices.json and apple website by item from LS
        #check to see where current item's storage falls numerically in matrix
        for sizeMult, size in enumerate(item.Sizes):
            if size.lower() in item.description.lower():
                break

        for deviceName, [deviceCurrent, deviceYear, deviceBasePrice, deviceCellPrice, deviceURL] in devices.items():
            #iterate through devices.json look for matching name look for base price or cell price
            if deviceName in item.description:
                if 'cell' in item.description.lower():
                    deviceBasePrice = deviceCellPrice
                #use device.json age to calculate from current and look for that age multiplier in age.json
                deviceAge = datetime.date.today().year - deviceYear
                for age, price in agePrice.items():
                    if deviceAge < int(age):
                        ageMult = price
                        break
                #if device is currently sold (documented in ages.json), load json from Apple web store and find price. Use URL key from devices.json
                if deviceCurrent:
                    browser.get(scrapeURL.format(deviceURL=deviceURL))
                    price = browser.find_element('id', 'metrics')
                    jsonPrice = price.text.replace('//','')
                    browser.minimize_window()
                    jsonPrice = jsonPrice.split('[[')
                    jsonPrice = jsonPrice[0] + '}}'
                    jsonPrice = jsonPrice.replace(',"sectionEngagement":','')
                    jsonPrice = jsonPrice.replace('"}]}}}}', '"}]}}')
                    jsonPrice = jsonPrice.replace('"shop"}}}}', '"shop"}}')
                    jsonPrice = json.loads(jsonPrice)

                    #Iterage through web prices and try to find match on current item.  Use deviceBasePrice to subtract from new price.  Detect if cellular
                    for product in jsonPrice["data"]["products"]:
                        if size.lower() in product["name"].lower():
                            if 'cell' in item.description.lower():
                                if 'cell' in product["name"].lower():
                                    applePrice = product["price"]["fullPrice"]
                                    break
                            else:
                                applePrice = product["price"]["fullPrice"]
                                break
                    devicePrice = applePrice - deviceBasePrice
                #device isn't new, dont use web lookup and generate price from base price, side and age multipliers
                else:
                    devicePrice = deviceBasePrice + (sizeMult * ageMult)
                debugOutput = "{description} Size:{sizeMult} Age:{deviceAge} Base:{deviceBasePrice} Item Price: {price}" 
                print(debugOutput.format(description=item.description, sizeMult=sizeMult, deviceAge=deviceAge, deviceBasePrice=deviceBasePrice, price=devicePrice))
                #load new price into all three LS item prices in Item object
                for itemPrice in item.Prices.ItemPrice:
                    if float(itemPrice.amount) != float(devicePrice):
                        itemPrice.amount = devicePrice
                        item.isModified = True
                #Item fucntion to make API put call and save price
                if item.isModified:
                    print(f"    Updating {item.description}")
                    classItem.Item.save_item_price(item)
                break