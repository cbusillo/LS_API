"""Class to import workorder objects from LS API"""
from datetime import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Generator, Optional, Self
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
    def from_json(cls, workorder_json: dict[str, Any]) -> Self:
        """Workorder object from dict"""

        if not isinstance(workorder_json, dict):
            raise ValueError("Workorder must be a dict: " + str(workorder_json))

        workorder_json_transformed = {
            "workorder_id": cls.safe_int(workorder_json.get("workorderID")),
            "time_in": cls.string_to_datetime(workorder_json.get("time_in")),
            "eta_out": cls.string_to_datetime(workorder_json.get("eta_out")),
            "note": workorder_json.get("note"),
            "warranty": workorder_json.get("warranty", "").lower() == "true",
            "tax": workorder_json.get("tax", "").lower() == "true",
            "archived": workorder_json.get("archived", "").lower() == "true",
            "time_stamp": cls.string_to_datetime(workorder_json.get("timeStamp")),
            "customer_id": cls.safe_int(workorder_json.get("customerID")),
            "serialized_id": cls.safe_int(workorder_json.get("serializedID")),
            "sale_id": cls.safe_int(workorder_json.get("saleID")),
            "sale_line_id": cls.safe_int(workorder_json.get("saleLineID")),
            "item_description": workorder_json.get("Serialized", {}).get("description", "").strip(),
            "status": workorder_json.get("WorkorderStatus", {}).get("name"),
        }
        return cls(**workorder_json_transformed)

    @classmethod
    def get_workorders(cls, date_filter: Optional[datetime] = None) -> Generator["Workorder", None, None]:
        """Run API auth."""
        for workorder in cls.get_entities_json(date_filter=date_filter, params=cls.default_params):
            yield Workorder.from_json(workorder)
