"""Item Class generated from LS API"""
from datetime import datetime
from decimal import Decimal
import re
import shlex
from typing import Any, Optional, Self, TYPE_CHECKING
from dataclasses import dataclass, field
from shiny_app.classes.ls_client import BaseLSEntity

if TYPE_CHECKING:
    from shiny_app.django_server.items.models import Item as ShinyItem


@dataclass
class Item(BaseLSEntity):
    """Item class from LS"""

    class_params = {"load_relations": '["ItemAttributes","ItemPrices"]'}

    @dataclass
    class ItemMatrix(BaseLSEntity):
        """Get full list of size attributes from LS table.
        Use these to import into individual items without a separate API call."""

        size_attributes = []  # type: ignore
        class_params = {"load_relations": '["ItemAttributeSet"]'}

        def __init__(self, size_attributes: Any):
            """Return items from json dict into SizeAttribute object."""
            super().__init__()
            self.item_matrix_id = int(size_attributes.get("itemMatrixID"))
            self.attribute2_value = size_attributes.get("attribute2Value") or ""

        @classmethod
        def from_json(cls, json: dict) -> Self:
            """Create an ItemMatrix object from a JSON dictionary."""
            return Item.ItemMatrix(size_attributes=json)

        @staticmethod
        def return_sizes(item_matrix_id: Optional[int]) -> list[str]:
            """Get sizes for individual item an return in list."""
            if item_matrix_id is None or item_matrix_id == 0:
                return []
            size_list: list[str] = []
            Item.ItemMatrix.check_size_attributes()
            for size in Item.ItemMatrix.size_attributes:
                if size.item_matrix_id == item_matrix_id:
                    size_list.append(size.attribute2_value)
            size_list.sort(key=Item.natural_keys)
            return size_list

        @classmethod
        def get_size_attributes(cls) -> list["Item.ItemMatrix"]:
            """Get data from API and return a dict."""
            item_matrix: list[Item.ItemMatrix] = []
            params = {"load_relations": '["ItemAttributeSet"]'}
            size_attributes = cls.get_entities_json(params=params)
            for matrix in size_attributes:
                if matrix["ItemAttributeSet"]["attributeName2"]:
                    for attribute in matrix["attribute2Values"]:
                        attr_obj = {
                            "itemMatrixID": matrix["itemMatrixID"],
                            "attribute2Value": attribute,
                        }
                        item_matrix.append(Item.ItemMatrix(attr_obj))
                        # itemList.append(Item.from_dict(item))
            return item_matrix

        @classmethod
        def check_size_attributes(cls):
            """Check if size attributes have been loaded."""
            if not cls.size_attributes:
                cls.size_attributes = Item.ItemMatrix.get_size_attributes()

    @dataclass
    class ItemAttribute:
        """Item Attribute"""

        attribute1: Optional[str] = None
        attribute2: Optional[str] = None
        attribute3: Optional[str] = None
        item_attribute_set_id: Optional[int] = None

    item_id: Optional[int] = None
    system_sku: Optional[str] = None
    default_cost: Optional[Decimal] = None
    average_cost: Optional[Decimal] = None
    tax: Optional[bool] = None
    archived: Optional[bool] = None
    item_type: Optional[str] = None
    serialized: Optional[bool] = None
    description: str = ""
    upc: Optional[str] = None
    custom_sku: Optional[str] = None
    manufacturer_sku: Optional[str] = None
    create_time: Optional[datetime] = None
    time_stamp: Optional[datetime] = None
    category_id: Optional[int] = None
    tax_class_id: Optional[int] = None
    item_matrix_id: Optional[int] = None
    manufacturer_id: Optional[int] = None
    default_vendor_id: Optional[int] = None
    price: Optional[Decimal] = None
    item_attributes: list[ItemAttribute] = field(default_factory=lambda: [])
    is_modified: Optional[bool] = None
    sizes: Optional[str] = None

    @staticmethod
    def atoi(text: str) -> int | str:
        """check if text is number for natrual number sort"""
        return int(text) if text.isdigit() else text

    @classmethod
    def natural_keys(cls, text: str) -> list[int | str]:
        """sort numbers like a human"""
        match text.lower():
            case "1tb":
                text = "1024GB"
            case "2tb":
                text = "2048GB"
            case _:
                pass
        return [cls.atoi(c) for c in re.split(r"(\d+)", text)]

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)

        if self.item_id and self.fetch_from_api:
            item_json = next(self.get_entities_json(entity_id=self.item_id))
            item = self.from_json(item_json)
            self.__dict__.update(item.__dict__)

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> Self:
        """Item object from dict"""
        if not isinstance(json, dict):
            raise TypeError("Item.from_json() requires a dict as input")

        default_price = None
        for price in json["Prices"]["ItemPrice"]:
            if price["useType"] == "Default":
                default_price = Decimal(price["amount"])
                break
        sizes = Item.ItemMatrix.return_sizes(cls.safe_int(json.get("itemMatrixID")))
        sizes_string = ""
        for size in sizes:
            sizes_string += f"{size}|"
        sizes_string = sizes_string[: -1 or None]

        item_json_transformed = {
            "item_id": cls.safe_int(json.get("itemID")),
            "system_sku": json.get("systemSku"),
            "default_cost": Decimal(json.get("defaultCost", 0)),
            "average_cost": Decimal(json.get("aveCost", 0)),
            "tax": json.get("tax", "").lower() == "true",
            "archived": json.get("archived", "").lower() == "true",
            "item_type": json.get("itemType"),
            "serialized": json.get("serialized", "").lower() == "true",
            "description": json.get("description", "").strip(),
            "upc": json.get("upc"),
            "custom_sku": json.get("customSku"),
            "manufacturer_sku": json.get("manufacturerSku"),
            "create_time": cls.string_to_datetime(json.get("createTime")),
            "time_stamp": cls.string_to_datetime(json.get("timeStamp")),
            "category_id": cls.safe_int(json.get("categoryID")),
            "tax_class_id": cls.safe_int(json.get("taxClassID")),
            "item_matrix_id": cls.safe_int(json.get("itemMatrixID")),
            "manufacturer_id": cls.safe_int(json.get("manufacturerID")),
            "default_vendor_id": cls.safe_int(json.get("defaultVendorID")),
            "item_attributes": json.get("ItemAttributes"),
            "price": default_price,
            "sizes": sizes_string,
        }
        return cls(**item_json_transformed)

    @classmethod
    def get_items_by_desciption(cls, descriptions: str | list[str]) -> list[Self]:
        """Return LS Item by searching description using OR and then filtering for all words"""
        if not isinstance(descriptions, list):
            descriptions = shlex.split(descriptions)
        item_list: list[Item] = []
        description = ""
        for word in descriptions:
            description += f"description=~,%{word}%|"
        params = cls.base_class_params
        params.update(cls.class_params)
        params["or"] = description
        for item in cls.get_entities_json(params=params):
            item_list.append(Item.from_json(item))

        filtered_list = [
            item for item in item_list if all(word.lower() in (item.description or "").lower() for word in descriptions)
        ]
        return filtered_list

    def update_item_price(self) -> None:
        """Call API put to update pricing."""
        if self.item_id is None:
            raise ValueError("Item ID is required to update item price")
        put_item = {
            "Prices": {
                "ItemPrice": [
                    {
                        "amount": f"{self.price}",
                        "useType": "Default",
                    },
                    {
                        "amount": f"{self.price}",
                        "useType": "MSRP",
                    },
                    {
                        "amount": f"{self.price}",
                        "useType": "Online",
                    },
                ]
            }
        }
        self.put_entity_json(self.item_id, put_item)

    def shiny_item_from_ls(self, shiny_item: "ShinyItem", start_time: datetime):
        """translation layer for LSItem to ShinyItem"""
        shiny_item.ls_item_id = self.item_id
        shiny_item.default_cost = self.default_cost or None
        shiny_item.average_cost = self.average_cost or None
        shiny_item.tax = self.tax
        shiny_item.price = self.price
        shiny_item.archived = self.archived
        shiny_item.item_type = self.item_type
        shiny_item.serialized = self.serialized
        shiny_item.description = self.description.strip().replace("  ", " ")
        shiny_item.upc = self.upc
        shiny_item.custom_sku = self.custom_sku
        shiny_item.manufacturer_sku = self.manufacturer_sku
        shiny_item.item_matrix_id = self.item_matrix_id
        shiny_item.item_attributes = None
        shiny_item.create_time = self.time_stamp or start_time
        shiny_item.update_time = start_time
        shiny_item.update_from_ls_time = start_time
        shiny_item.sizes = self.sizes

        return shiny_item, None
