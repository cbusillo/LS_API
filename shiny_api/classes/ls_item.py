"""Item Class generated from LS API"""
import os
import re
import shlex
from typing import Any
from dataclasses import dataclass
from shiny_api.modules.connect_ls import generate_ls_access, get_data, put_data
from shiny_api.modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")


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
    return [atoi(c) for c in re.split(r"(\d+)", text)]


@dataclass
class SizeAttributes:
    """Get full list of size attributes from LS table.  Use these to import into individual items without a separate API call."""

    SIZE_ATTRIBUTES = []

    def __init__(self, obj: Any):
        """Return items from json dict into SizeAttribute object."""
        self.item_matrix_id = str(obj.get("itemMatrixID"))
        self.attribute2_value = str(obj.get("attribute2Value"))

    @staticmethod
    def return_sizes(item_matrix_id: str):
        """Get sizes for individual item an return in list."""
        size_list = []
        SizeAttributes.check_size_attributes()
        for size in SizeAttributes.SIZE_ATTRIBUTES:
            if size.item_matrix_id == item_matrix_id:
                size_list.append(size.attribute2_value)
        size_list.sort(key=natural_keys)
        return size_list

    @staticmethod
    def get_size_attributes():
        """Get data from API and return a dict."""
        current_url = config.LS_URLS["itemMatrix"]
        item_matrix: list[SizeAttributes] = []
        while current_url:
            response = get_data(current_url, current_params={"load_relations": '["ItemAttributeSet"]', "limit": 100})
            for matrix in response.json().get("ItemMatrix"):
                if matrix["ItemAttributeSet"]["attributeName2"]:
                    for attribute in matrix["attribute2Values"]:
                        attr_obj = {
                            "itemMatrixID": matrix["itemMatrixID"],
                            "attribute2Value": attribute,
                        }
                        item_matrix.append(SizeAttributes(attr_obj))
                        # itemList.append(Item.from_dict(item))
            current_url = response.json()["@attributes"]["next"]
        return item_matrix

    @classmethod
    def check_size_attributes(cls):
        """Check if size attributes have been loaded."""
        if not cls.SIZE_ATTRIBUTES:
            cls.SIZE_ATTRIBUTES = SizeAttributes.get_size_attributes()


@dataclass
class ItemAttributes:
    """Attribute object for item.  This holds the specific attribute on item."""

    def __init__(self, obj: Any):
        """Load ItemAttributes object from json dict."""
        if obj is None:
            return None
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

    def __init__(self, item_id: int = None, ls_item: Any = None):
        """Item from dict"""
        if ls_item is None:
            if item_id is None:
                raise ValueError("Must provide item_id or ls_item")
            self.item_id = item_id
            ls_item = self._get_item()
        self.item_id: int = ls_item.get("itemID")

        self.system_sku = str(ls_item.get("systemSku"))
        self.default_cost = str(ls_item.get("defaultCost"))
        self.avg_cost = str(ls_item.get("avgCost"))
        self.discountable = str(ls_item.get("discountable"))
        self.tax = str(ls_item.get("tax"))
        self.archived = str(ls_item.get("archived"))
        self.item_type = str(ls_item.get("itemType"))
        self.serialized = str(ls_item.get("serialized"))
        self.description = str(ls_item.get("description"))
        self.model_year = str(ls_item.get("modelYear"))
        self.upc = str(ls_item.get("upc"))
        self.ean = str(ls_item.get("ean"))
        self.custom_sku = str(ls_item.get("customSku"))
        self.manufacturer_sku = str(ls_item.get("manufacturerSku"))
        self.create_time = str(ls_item.get("createTime"))
        self.time_stamp = str(ls_item.get("timeStamp"))
        self.publish_to_ecom = str(ls_item.get("publishToEcom"))
        self.category_id = str(ls_item.get("categoryID"))
        self.tax_class_id = str(ls_item.get("taxClassID"))
        self.department_id = str(ls_item.get("departmentID"))
        self.item_matrix_id = str(ls_item.get("itemMatrixID"))
        self.manufacturer_id = str(ls_item.get("manufacturerID"))
        self.season_id = str(ls_item.get("seasonID"))
        self.default_vendor_id = str(ls_item.get("defaultVendorID"))
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
        put_data(config.LS_URLS["item"].format(itemID=self.item_id), put_item)

    def _get_item(self):
        """Return LS Item object by item ID"""
        current_url = config.LS_URLS["item"]
        response = get_data(current_url.format(itemID=self.item_id), {"load_relations": '["ItemAttributes"]'})
        return response.json().get("Item")


class Items:
    """Return list of Item objects from LS"""

    def __init__(self, descriptions: list[str] = None, categories: list[str] = None):
        self.item_list: list[Item] = []
        if descriptions is not None:
            if not isinstance(descriptions, list):
                descriptions = shlex.split(descriptions)
            self._get_items_by_desciption(descriptions)
            return
        if categories is not None:
            self._get_items_by_category(categories)
            return
        self._get_all_items()

    def __repr__(self):
        return f"Items({len(self)})"

    def _get_all_items(self):
        """Run API auth."""
        generate_ls_access()
        current_url = config.LS_URLS["items"]
        while current_url:
            response = get_data(current_url, {"load_relations": '["ItemAttributes"]', "limit": 100})
            for item in response.json().get("Item"):
                self.item_list.append(Item(ls_item=item))
            current_url = response.json()["@attributes"]["next"]

    def _get_items_by_category(self, categories: list[str] = None):
        """Run API auth."""
        generate_ls_access()
        for category in categories:
            current_url = config.LS_URLS["items"]
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
                    self.item_list.append(Item(ls_item=item))
                current_url = response.json()["@attributes"]["next"]

    def _get_items_by_desciption(self, descriptions: list[str]):
        """Return LS Item by searching description using OR and then filtering for all words"""

        item_list: list[Item] = []
        current_url = config.LS_URLS["items"]
        description = ""
        for word in descriptions:
            description += f"description=~,%{word}%|"
        while current_url:
            response = get_data(current_url, {"or": description, "load_relations": '["ItemAttributes"]'})
            current_url = response.json()["@attributes"]["next"]
            if response.json().get("Item") is None:
                return
            for item in response.json().get("Item"):
                item_list.append(Item(ls_item=item))

        filtered_list = [item for item in item_list if all(word.lower() in item.description.lower() for word in descriptions)]
        self.item_list.extend(filtered_list)


if __name__ == "__main__":
    print(Items())
