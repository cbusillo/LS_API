import os
import re
import json
from typing import List, Any
from dataclasses import dataclass

from modules.connect import urls, accessHeader, generate_access, get_data, put_data

print("Importing {}...".format(os.path.basename(__file__)))

categories = [173, 171]  #iterate through categories 171 iPads 173 iPhones 

def atoi(text):
    #check if text is number for natrual number sort
    return int(text) if text.isdigit() else text

def natural_keys(text):
    #sort numbers like a human
    match text.lower():
        case '1tb':
            text = '1024GB'
        case '2tb':
            text = '2048GB'
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def toJSON(tojson):
    return json.dumps(tojson, default=lambda o: o.__dict__, sort_keys=True, indent=None, separators=(', ', ': '))

@dataclass
class SizeAttributes:
    #get full list of size attributes from LS table.  Use these to import into individual items without a separate API call
    itemMatrixID: str
    description: str

    def return_sizes(itemMatrixID):
        #get sizes for individual item an return in list.
        sizeList = []
        for size in sizeAttributes:
            if size.itemMatrixID == itemMatrixID:
                sizeList.append(size.description)
        sizeList.sort(key=natural_keys)
        return sizeList

    @staticmethod
    def from_dict(obj: Any) -> 'SizeAttributes':
        #return items from json dict into SizeAttribute object
        _itemMatrixID = str(obj.get("itemMatrixID"))
        _attribute2Value = str(obj.get("attribute2Value"))
        return SizeAttributes(_itemMatrixID, _attribute2Value)

    @staticmethod
    def get_size_attributes():
        #get data from API and return a 
        currentURL = urls["itemMatrix"]
        itemMatrix: List[SizeAttributes] = []
        while currentURL:
            response = get_data(currentURL,{'load_relations':'["ItemAttributeSet"]', 'limit': 100})
            for matrix in response.json().get("ItemMatrix"):
                if matrix['ItemAttributeSet']['attributeName2']:
                    for attribute in matrix["attribute2Values"]:
                        attrObj = {'itemMatrixID': matrix["itemMatrixID"], 'attribute2Value': attribute }
                        itemMatrix.append(SizeAttributes.from_dict(attrObj))
                        #itemList.append(Item.from_dict(item))
            currentURL = response.json()["@attributes"]["next"]
        return itemMatrix

@dataclass
class ItemAttributes:
    #attribute object for item.  This holds the specific attribute on item
    attribute1: str
    attribute2: str
    attribute3: str
    itemAttributeSetID: str

    @staticmethod
    def from_dict(obj: Any) -> 'ItemAttributes':
        #load ItemAttributes object from json dict
        _attribute1 = str(obj.get("attribute1"))
        _attribute2 = str(obj.get("attribute2"))
        _attribute3 = str(obj.get("attribute3"))
        _itemAttributeSetID = str(obj.get("itemAttributeSetID"))
        return ItemAttributes(_attribute1, _attribute2, _attribute3, _itemAttributeSetID)

@dataclass
class ItemPrice:
    amount: str
    useTypeID: str
    useType: str

    @staticmethod
    def from_dict(obj: Any) -> 'ItemPrice':
        _amount = str(obj.get("amount"))
        _useTypeID = str(obj.get("useTypeID"))
        _useType = str(obj.get("useType"))
        return ItemPrice(_amount, _useTypeID, _useType)

@dataclass
class Prices:
    ItemPrice: List[ItemPrice]

    @staticmethod
    def from_dict(obj: Any) -> 'Prices':
        _ItemPrice = [ItemPrice.from_dict(y) for y in obj.get("ItemPrice")]
        return Prices(_ItemPrice)

@dataclass
class Item:
    #item object generated from json dict
    itemID: str
    systemSku: str
    defaultCost: str
    avgCost: str
    discountable: str
    tax: str
    archived: str
    itemType: str
    serialized: str
    description: str
    modelYear: str
    upc: str
    ean: str
    customSku: str
    manufacturerSku: str
    createTime: str
    timeStamp: str
    publishToEcom: str
    categoryID: str
    taxClassID: str
    departmentID: str
    itemMatrixID: str
    manufacturerID: str
    seasonID: str
    defaultVendorID: str
    ItemAttributes: ItemAttributes
    Prices: Prices
    Sizes: List
    isModified: bool

    @staticmethod
    def from_dict(obj: Any) -> 'Item':
        #return individual items from json dict to an Item object
        _itemID = str(obj.get("itemID"))
        _systemSku = str(obj.get("systemSku"))
        _defaultCost = str(obj.get("defaultCost"))
        _avgCost = str(obj.get("avgCost"))
        _discountable = str(obj.get("discountable"))
        _tax = str(obj.get("tax"))
        _archived = str(obj.get("archived"))
        _itemType = str(obj.get("itemType"))
        _serialized = str(obj.get("serialized"))
        _description = str(obj.get("description"))
        _modelYear = str(obj.get("modelYear"))
        _upc = str(obj.get("upc"))
        _ean = str(obj.get("ean"))
        _customSku = str(obj.get("customSku"))
        _manufacturerSku = str(obj.get("manufacturerSku"))
        _createTime = str(obj.get("createTime"))
        _timeStamp = str(obj.get("timeStamp"))
        _publishToEcom = str(obj.get("publishToEcom"))
        _categoryID = str(obj.get("categoryID"))
        _taxClassID = str(obj.get("taxClassID"))
        _departmentID = str(obj.get("departmentID"))
        _itemMatrixID = str(obj.get("itemMatrixID"))
        _manufacturerID = str(obj.get("manufacturerID"))
        _seasonID = str(obj.get("seasonID"))
        _defaultVendorID = str(obj.get("defaultVendorID"))
        _ItemAttributes = ItemAttributes.from_dict(obj.get("ItemAttributes"))
        _Prices = Prices.from_dict(obj.get("Prices"))
        _Sizes = SizeAttributes.return_sizes(obj.get("itemMatrixID"))
        _isModified = False
        return Item(_itemID, _systemSku, _defaultCost, _avgCost, _discountable, _tax, _archived, _itemType, _serialized, _description, _modelYear, _upc, _ean, _customSku, _manufacturerSku, _createTime, _timeStamp, _publishToEcom, _categoryID, _taxClassID, _departmentID, _itemMatrixID, _manufacturerID, _seasonID, _defaultVendorID, _ItemAttributes, _Prices, _Sizes, _isModified)
    
    @staticmethod
    def save_item_price(item: 'Item'):
        #call API put to update pricing
        #TODO use generated payload instead of manual
        putItem = { "Prices": {"ItemPrice": [
                        {"amount": "{}".format(item.Prices.ItemPrice[0].amount), "useType": "Default"},
                        {"amount": "{}".format(item.Prices.ItemPrice[0].amount), "useType": "MSRP"},
                        {"amount": "{}".format(item.Prices.ItemPrice[0].amount), "useType": "Online"}]}}
        put_data(urls["itemPut"].format(itemID = item.itemID), putItem)

    @staticmethod
    def get_items() -> 'List[Item]':
        #Run API auth
        generate_access()
        #API call to get all items.  Walk through categories and pages.  Convert from json dict to Item object and add to itemList list.
        itemList: List[Item] = []
        for category in categories:
            currentURL = urls["item"]
            while currentURL:
                response =  get_data(currentURL,{'categoryID' : category,'load_relations':'["ItemAttributes"]', 'limit': 100})
                for item in response.json().get("Item"):
                    itemList.append(Item.from_dict(item))
                currentURL = response.json()["@attributes"]["next"]
        
        return itemList


#load attributes before main program runs
sizeAttributes = SizeAttributes.get_size_attributes()