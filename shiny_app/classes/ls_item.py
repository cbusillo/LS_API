"""Item Class generated from LS API"""
from datetime import datetime
from decimal import Decimal
import re
import shlex
from typing import Any, Generator, Optional, Self
from dataclasses import dataclass, field
from shiny_app.classes.ls_client import BaseLSEntity


@dataclass
class Item(BaseLSEntity):
    """Item class from LS"""

    default_params = {"load_relations": '["ItemAttributes","ItemPrices"]'}

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
    def from_json(cls, item_json: dict[str, Any]) -> Self:
        """Item object from dict"""
        if not isinstance(item_json, dict):
            raise TypeError("Item.from_json() requires a dict as input")

        default_price = None
        for price in item_json["Prices"]["ItemPrice"]:
            if price["useType"] == "Default":
                default_price = Decimal(price["amount"])
                break

        item_json_transformed = {
            "item_id": cls.safe_int(item_json.get("itemID")),
            "system_sku": item_json.get("systemSku"),
            "default_cost": Decimal(item_json.get("defaultCost", 0)),
            "average_cost": Decimal(item_json.get("aveCost", 0)),
            "tax": item_json.get("tax", "").lower() == "true",
            "archived": item_json.get("archived", "").lower() == "true",
            "item_type": item_json.get("itemType"),
            "serialized": item_json.get("serialized", "").lower() == "true",
            "description": item_json.get("description", "").strip(),
            "upc": item_json.get("upc"),
            "custom_sku": item_json.get("customSku"),
            "manufacturer_sku": item_json.get("manufacturerSku"),
            "create_time": cls.string_to_datetime(item_json.get("createTime")),
            "time_stamp": cls.string_to_datetime(item_json.get("timeStamp")),
            "category_id": cls.safe_int(item_json.get("categoryID")),
            "tax_class_id": cls.safe_int(item_json.get("taxClassID")),
            "item_matrix_id": cls.safe_int(item_json.get("itemMatrixID")),
            "manufacturer_id": cls.safe_int(item_json.get("manufacturerID")),
            "default_vendor_id": cls.safe_int(item_json.get("defaultVendorID")),
            "item_attributes": item_json.get("ItemAttributes"),
            "price": default_price,
        }
        return cls(**item_json_transformed)

    @classmethod
    def get_items(
        cls, date_filter: Optional[datetime] = None, categories: list[int] | int | None = None
    ) -> Generator[Self, None, None]:
        """Run API auth."""

        if categories:
            if not isinstance(categories, list):
                categories = [categories]
        else:
            categories = [0]

        for category_id in categories:
            params = cls.default_params
            if category_id != 0:
                params = {"categoryID": category_id}
            for item in cls.get_entities_json(date_filter=date_filter, params=params):
                yield Item.from_json(item)

    @classmethod
    def get_items_by_desciption(cls, descriptions: str | list[str]) -> list[Self]:
        """Return LS Item by searching description using OR and then filtering for all words"""
        if not isinstance(descriptions, list):
            descriptions = shlex.split(descriptions)
        item_list: list[Item] = []
        description = ""
        for word in descriptions:
            description += f"description=~,%{word}%|"
        params = cls.default_params
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
