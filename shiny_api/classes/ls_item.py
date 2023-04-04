"""Item Class generated from LS API"""
from datetime import datetime
from decimal import Decimal
import re
import shlex
from typing import Any
from dataclasses import dataclass
from shiny_api.classes.ls_client import Client, string_to_datetime
from shiny_api.modules.load_config import Config


def atoi(text: str):
    """check if text is number for natrual number sort"""
    return int(text) if text.isdigit() else text


def natural_keys(text: str):
    """sort numbers like a human"""
    match text.lower():
        case "1tb":
            text = "1024GB"
        case "2tb":
            text = "2048GB"
        case _:
            pass
    return [atoi(c) for c in re.split(r"(\d+)", text)]


@dataclass
class SizeAttributes:
    """Get full list of size attributes from LS table.
    Use these to import into individual items without a separate API call."""

    size_attributes = []  # type: ignore

    def __init__(self, obj: Any):
        """Return items from json dict into SizeAttribute object."""
        self.item_matrix_id = str(obj.get("itemMatrixID"))
        self.attribute2_value = str(obj.get("attribute2Value"))

    @staticmethod
    def return_sizes(item_matrix_id: str) -> list[str]:
        """Get sizes for individual item an return in list."""
        size_list: list[str] = []
        SizeAttributes.check_size_attributes()
        for size in SizeAttributes.size_attributes:
            if size.item_matrix_id == item_matrix_id:
                size_list.append(size.attribute2_value)
        size_list.sort(key=natural_keys)
        return size_list

    @staticmethod
    def get_size_attributes() -> list["SizeAttributes"]:
        """Get data from API and return a dict."""
        item_matrix: list[SizeAttributes] = []
        client = Client()
        for matrix in client.get_size_attributes_json():
            if matrix["ItemAttributeSet"]["attributeName2"]:
                for attribute in matrix["attribute2Values"]:
                    attr_obj = {
                        "itemMatrixID": matrix["itemMatrixID"],
                        "attribute2Value": attribute,
                    }
                    item_matrix.append(SizeAttributes(attr_obj))
                    # itemList.append(Item.from_dict(item))
        return item_matrix

    @classmethod
    def check_size_attributes(cls):
        """Check if size attributes have been loaded."""
        if not cls.size_attributes:
            cls.size_attributes = SizeAttributes.get_size_attributes()


@dataclass
class ItemAttributes:
    """Attribute object for item.  This holds the specific attribute on item."""

    def __init__(self, obj: Any):
        """Load ItemAttributes object from json dict."""
        if obj is None:
            return
        self.attribute1 = str(obj.get("attribute1"))
        self.attribute2 = str(obj.get("attribute2"))
        self.attribute3 = str(obj.get("attribute3"))
        self.item_attribute_set_id = str(obj.get("itemAttributeSetID"))


@dataclass
class ItemPrice:
    """ItemPrice class from LS"""

    def __init__(self, obj: Any):
        """ItemPrice from dict"""
        self.amount = str(obj.get("amount"))
        self.use_type_id = str(obj.get("useTypeID"))
        self.use_type = str(obj.get("useType"))


@dataclass
class Prices:
    """Prices class from LS"""

    def __init__(self, obj: Any):
        """Prices from dict"""
        self.item_price = [ItemPrice(y) for y in obj.get("ItemPrice")]


@dataclass
class Item:
    """Item class from LS"""

    client = Client()

    def __init__(self, item_id: int = 0, ls_item: Any = None):

        if ls_item is None:
            if item_id == 0:
                raise ValueError("Must provide item_id or ls_item")
            ls_item = self.client.get_item_json(item_id)
        if ls_item is None:
            self.item_id = 0
            return

        self.item_id = int(ls_item.get("itemID"))

        self.system_sku = int(ls_item.get("systemSku"))
        self.default_cost = Decimal(ls_item.get("defaultCost"))
        self.avg_cost = Decimal(ls_item.get("avgCost"))
        self.tax = bool(ls_item.get("tax").lower() == "true")
        self.archived = bool(ls_item.get("archived").lower() == "true")
        self.item_type = str(ls_item.get("itemType"))
        self.serialized = bool(ls_item.get("serialized").lower() == "true")
        self.description = str(ls_item.get("description"))
        self.upc = ls_item.get("upc")
        self.custom_sku = str(ls_item.get("customSku"))
        self.manufacturer_sku = str(ls_item.get("manufacturerSku"))
        self.create_time = string_to_datetime(ls_item.get("createTime"))
        self.time_stamp = string_to_datetime(ls_item.get("timeStamp"))
        self.category_id = int(ls_item.get("categoryID"))
        self.tax_class_id = int(ls_item.get("taxClassID"))
        self.item_matrix_id = int(ls_item.get("itemMatrixID"))
        self.manufacturer_id = int(ls_item.get("manufacturerID"))
        self.default_vendor_id = int(ls_item.get("defaultVendorID"))
        self.item_attributes = ItemAttributes(ls_item.get("ItemAttributes"))
        self.prices = Prices(ls_item.get("Prices"))
        self.sizes = SizeAttributes.return_sizes(ls_item.get("itemMatrixID"))
        self.is_modified = False

    def __repr__(self):
        return f"{self.item_id} - {self.description}"

    def save_item_price(self):
        """Call API put to update pricing."""
        put_item = {
            "Prices": {
                "ItemPrice": [
                    {
                        "amount": f"{self.prices.item_price[0].amount}",
                        "useType": "Default",
                    },
                    {
                        "amount": f"{self.prices.item_price[0].amount}",
                        "useType": "MSRP",
                    },
                    {
                        "amount": f"{self.prices.item_price[0].amount}",
                        "useType": "Online",
                    },
                ]
            }
        }
        url = Config.LS_URLS["item"].format(itemID=self.item_id)
        self.client.put(url, json=put_item)

    @classmethod
    def get_all_items(cls, date_filter: datetime | None = None):
        """Run API auth."""
        for item in cls.client.get_items_json(date_filter=date_filter):
            yield Item(ls_item=item)

    @classmethod
    def get_items_by_category(cls, categories: list[str], date_filter: datetime | None = None):
        """Run API auth."""
        if not isinstance(categories, list):
            categories = [categories]
        for category in categories:
            for item in cls.client.get_items_json(category_id=category, date_filter=date_filter):
                yield Item(ls_item=item)

    @classmethod
    def get_items_by_desciption(cls, descriptions: str | list[str]):
        """Return LS Item by searching description using OR and then filtering for all words"""
        if not isinstance(descriptions, list):
            descriptions = shlex.split(descriptions)
        item_list: list[Item] = []
        description = ""
        for word in descriptions:
            description += f"description=~,%{word}%|"

            for item in cls.client.get_items_json(description=description):
                item_list.append(Item(ls_item=item))

        filtered_list = [item for item in item_list if all(word.lower() in item.description.lower() for word in descriptions)]
        return filtered_list


if __name__ == "__main__":
    test_items = Item.get_all_items()
    for index, test_item in enumerate(test_items):
        print(test_item)
        if index == 4:
            break
