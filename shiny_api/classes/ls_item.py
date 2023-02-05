"""Item Class generated from LS API"""
import os
import re
import json
from typing import List, Any
from dataclasses import dataclass
from shiny_api.modules.connect_ls import generate_ls_access, get_data, put_data
from shiny_api.modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")


def atoi(text):
    """check if text is number for natrual number sort"""
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """sort numbers like a human"""
    match text.lower():
        case "1tb":
            text = "1024GB"
        case "2tb":
            text = "2048GB"
    return [atoi(c) for c in re.split(r"(\d+)", text)]


def to_json(tojson):
    """Convert string to JSON"""
    return json.dumps(
        tojson,
        default=lambda o: o.__dict__,
        sort_keys=True,
        indent=None,
        separators=(", ", ": "),
    )


@dataclass
class SizeAttributes:
    """Get full list of size attributes from LS table.  Use these to import into individual items without a separate API call."""

    item_matrix_id: str
    description: str

    def return_sizes(self):
        """Get sizes for individual item an return in list."""
        size_list = []
        for size in sizeAttributes:
            if size.item_matrix_id == self:
                size_list.append(size.description)
        size_list.sort(key=natural_keys)
        return size_list

    @staticmethod
    def from_dict(obj: Any) -> "SizeAttributes":
        """Return items from json dict into SizeAttribute object."""
        _item_matrix_id = str(obj.get("itemMatrixID"))
        _attribute2_value = str(obj.get("attribute2Value"))
        return SizeAttributes(_item_matrix_id, _attribute2_value)

    @staticmethod
    def get_size_attributes():
        """Get data from API and return a dict."""
        current_url = config.LS_URLS["itemMatrix"]
        item_matrix: List[SizeAttributes] = []
        while current_url:
            response = get_data(current_url, current_params={"load_relations": '["ItemAttributeSet"]', "limit": 100})
            for matrix in response.json().get("ItemMatrix"):
                if matrix["ItemAttributeSet"]["attributeName2"]:
                    for attribute in matrix["attribute2Values"]:
                        attr_obj = {
                            "itemMatrixID": matrix["itemMatrixID"],
                            "attribute2Value": attribute,
                        }
                        item_matrix.append(SizeAttributes.from_dict(attr_obj))
                        # itemList.append(Item.from_dict(item))
            current_url = response.json()["@attributes"]["next"]
        return item_matrix


@dataclass
class ItemAttributes:
    """Attribute object for item.  This holds the specific attribute on item."""

    attribute1: str
    attribute2: str
    attribute3: str
    item_attribute_set_id: str

    @staticmethod
    def from_dict(obj: Any) -> "ItemAttributes":
        """Load ItemAttributes object from json dict."""
        _attribute1 = str(obj.get("attribute1"))
        _attribute2 = str(obj.get("attribute2"))
        _attribute3 = str(obj.get("attribute3"))
        _item_attribute_set_id = str(obj.get("itemAttributeSetID"))
        return ItemAttributes(_attribute1, _attribute2, _attribute3, _item_attribute_set_id)


@dataclass
class ItemPrice:
    """ItemPrice class from LS"""

    amount: str
    use_type_id: str
    use_type: str

    @staticmethod
    def from_dict(obj: Any) -> "ItemPrice":
        """ItemPrice from dict"""
        _amount = str(obj.get("amount"))
        _use_type_id = str(obj.get("useTypeID"))
        _use_type = str(obj.get("useType"))
        return ItemPrice(_amount, _use_type_id, _use_type)


@dataclass
class Prices:
    """Prices class from LS"""

    item_price: List[ItemPrice]

    @staticmethod
    def from_dict(obj: Any) -> "Prices":
        """Prices from dict"""
        _item_price = [ItemPrice.from_dict(y) for y in obj.get("ItemPrice")]
        return Prices(_item_price)


@dataclass
class Item:
    """Item class from LS"""

    # item object generated from json dict
    item_id: str
    system_sku: str
    default_cost: str
    avg_cost: str
    discountable: str
    tax: str
    archived: str
    item_type: str
    serialized: str
    description: str
    model_year: str
    upc: str
    ean: str
    custom_sku: str
    manufacturer_sku: str
    create_time: str
    time_stamp: str
    publish_to_ecom: str
    category_id: str
    taxclass_id: str
    department_id: str
    item_matrix_id: str
    manufacturer_id: str
    season_id: str
    default_vendor_id: str
    item_attributes: ItemAttributes
    prices: Prices
    sizes: List
    is_modified: bool

    @staticmethod
    def from_dict(obj: Any) -> "Item":
        """Item from dict"""
        # return individual items from json dict to an Item object
        _item_id = str(obj.get("itemID"))
        _system_sku = str(obj.get("systemSku"))
        _default_cost = str(obj.get("defaultCost"))
        _avg_cost = str(obj.get("avgCost"))
        _discountable = str(obj.get("discountable"))
        _tax = str(obj.get("tax"))
        _archived = str(obj.get("archived"))
        _item_type = str(obj.get("itemType"))
        _serialized = str(obj.get("serialized"))
        _description = str(obj.get("description"))
        _model_year = str(obj.get("modelYear"))
        _upc = str(obj.get("upc"))
        _ean = str(obj.get("ean"))
        _custom_sku = str(obj.get("customSku"))
        _manufacturer_sku = str(obj.get("manufacturerSku"))
        _create_time = str(obj.get("createTime"))
        _time_stamp = str(obj.get("timeStamp"))
        _publish_to_ecom = str(obj.get("publishToEcom"))
        _category_id = str(obj.get("categoryID"))
        _tax_class_id = str(obj.get("taxClassID"))
        _department_id = str(obj.get("departmentID"))
        _item_matrix_id = str(obj.get("itemMatrixID"))
        _manufacturer_id = str(obj.get("manufacturerID"))
        _season_id = str(obj.get("seasonID"))
        _default_vendor_id = str(obj.get("defaultVendorID"))
        _item_attributes = ItemAttributes.from_dict(obj.get("ItemAttributes"))
        _prices = Prices.from_dict(obj.get("Prices"))
        _sizes = SizeAttributes.return_sizes(obj.get("itemMatrixID"))
        _is_modified = False
        return Item(
            _item_id,
            _system_sku,
            _default_cost,
            _avg_cost,
            _discountable,
            _tax,
            _archived,
            _item_type,
            _serialized,
            _description,
            _model_year,
            _upc,
            _ean,
            _custom_sku,
            _manufacturer_sku,
            _create_time,
            _time_stamp,
            _publish_to_ecom,
            _category_id,
            _tax_class_id,
            _department_id,
            _item_matrix_id,
            _manufacturer_id,
            _season_id,
            _default_vendor_id,
            _item_attributes,
            _prices,
            _sizes,
            _is_modified,
        )

    @staticmethod
    def save_item_price(item: "Item"):
        """Call API put to update pricing."""
        # TODO use generated payload instead of manual
        put_item = {
            "Prices": {
                "ItemPrice": [
                    {
                        "amount": f"{item.prices.item_price[0].amount}",
                        "useType": "Default",
                    },
                    {
                        "amount": f"{item.prices.item_price[0].amount}",
                        "useType": "MSRP",
                    },
                    {
                        "amount": f"{item.prices.item_price[0].amount}",
                        "useType": "Online",
                    },
                ]
            }
        }
        put_data(config.LS_URLS["itemPut"].format(itemID=item.item_id), put_item)

    @staticmethod
    def get_items() -> "List[Item]":
        """Run API auth."""
        generate_ls_access()
        # API call to get all items.  Walk through categories and pages.
        # Convert from json dict to Item object and add to itemList list.
        item_list: List[Item] = []
        for category in config.DEVICE_CATEGORIES_FOR_PRICE:
            current_url = config.LS_URLS["item"]
            while current_url:
                response = get_data(
                    current_url,
                    {
                        "categoryID": category,
                        "load_relations": '["ItemAttributes"]',
                        "limit": 100,
                    },
                )
                for item in response.json().get("Item"):
                    item_list.append(Item.from_dict(item))
                current_url = response.json()["@attributes"]["next"]

        return item_list


# load attributes before main program runs
sizeAttributes = SizeAttributes.get_size_attributes()
