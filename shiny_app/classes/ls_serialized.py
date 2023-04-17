"""Serial class from LS""" ""
from typing import Any, Optional, Self
from datetime import datetime
from dataclasses import dataclass
from shiny_app.classes.ls_client import BaseLSEntity


@dataclass
class Serialized(BaseLSEntity):
    """Serial class from LS"""

    default_params = {}

    serial_id: Optional[int] = None
    value_1: Optional[str] = None
    value_2: Optional[str] = None
    serial_number: Optional[str] = None
    description: Optional[str] = None
    item_id: Optional[int] = None
    customer_id: Optional[int] = None
    time_stamp: Optional[datetime] = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)

        if self.serial_id and self.fetch_from_api:
            serial_json = next(self.get_entities_json(entity_id=self.serial_id))
            serial = self.from_json(serial_json)
            self.__dict__.update(serial.__dict__)

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> Self:
        if not isinstance(json, dict):
            raise TypeError("serial_json must be a dict")

        serial_json_transformed = {
            "serial_id": cls.safe_int(json.get("serialID")),
            "value_1": json.get("colorName"),
            "value_2": json.get("sizeName"),
            "serial_number": json.get("serial"),
            "description": json.get("description"),
            "item_id": cls.safe_int(json.get("itemID")),
            "customer_id": cls.safe_int(json.get("customerID")),
            "time_stamp": cls.string_to_datetime(json.get("timeStamp")),
        }

        return cls(**serial_json_transformed)
