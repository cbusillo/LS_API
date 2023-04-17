"""Class to import workorder objects from LS API"""
from datetime import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional, Self
from shiny_app.classes.ls_client import BaseLSEntity


@dataclass
class Workorder(BaseLSEntity):
    """Workorder object from LS"""

    default_params = {"load_relations": '["Serialized", "WorkorderStatus","WorkorderItems","WorkorderLines"]'}

    workorder_id: Optional[int] = None
    time_in: Optional[datetime] = None
    eta_out: Optional[datetime] = None
    note: str = ""
    warranty: Optional[bool] = None
    tax: Optional[bool] = None
    archived: Optional[bool] = None
    time_stamp: Optional[datetime] = None
    customer_id: Optional[int] = None
    serialized_id: Optional[int] = None
    sale_id: Optional[int] = None
    sale_line_id: Optional[int] = None
    item_description: Optional[str] = None
    status: Optional[str] = None
    total: Optional[Decimal] = None

    def __init__(self, *args, **kwargs):
        """Workorder object from dict"""
        super().__init__()
        self.__dict__.update(kwargs)

        if self.workorder_id and self.fetch_from_api:
            workorder_json = next(self.get_entities_json(entity_id=self.workorder_id))
            workorder = self.from_json(workorder_json)
            self.__dict__.update(workorder.__dict__)

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> Self:
        """Workorder object from dict"""

        if not isinstance(json, dict):
            raise ValueError("Workorder must be a dict: " + str(json))

        workorder_json_transformed = {
            "workorder_id": cls.safe_int(json.get("workorderID")),
            "time_in": cls.string_to_datetime(json.get("time_in")),
            "eta_out": cls.string_to_datetime(json.get("eta_out")),
            "note": json.get("note"),
            "warranty": json.get("warranty", "").lower() == "true",
            "tax": json.get("tax", "").lower() == "true",
            "archived": json.get("archived", "").lower() == "true",
            "time_stamp": cls.string_to_datetime(json.get("timeStamp")),
            "customer_id": cls.safe_int(json.get("customerID")),
            "serialized_id": cls.safe_int(json.get("serializedID")),
            "sale_id": cls.safe_int(json.get("saleID")),
            "sale_line_id": cls.safe_int(json.get("saleLineID")),
            "item_description": json.get("Serialized", {}).get("description", "").strip(),
            "status": json.get("WorkorderStatus", {}).get("name"),
        }
        return cls(**workorder_json_transformed)
