"""Class to import workorder objects from LS API"""
from datetime import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional, Self, TYPE_CHECKING
from shiny_app.classes.ls_client import BaseLSEntity

if TYPE_CHECKING:
    from shiny_app.django_server.workorders.models import Workorder as ShinyWorkorder


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

    def shiny_workorder_from_ls(self, shiny_workorder: "ShinyWorkorder", start_time: datetime):
        """Convert LS Workorder to Shiny Workorder"""
        # pylint: disable=import-outside-toplevel
        from shiny_app.django_server.customers.models import Customer as ShinyCustomer

        shiny_workorder.ls_workorder_id = self.workorder_id
        shiny_workorder.time_in = self.time_in
        shiny_workorder.eta_out = self.eta_out
        shiny_workorder.note = self.note
        shiny_workorder.warranty = self.warranty
        shiny_workorder.tax = self.tax
        shiny_workorder.archived = self.archived
        shiny_workorder.update_time = start_time
        shiny_workorder.update_from_ls_time = start_time
        # shiny_workorder.total = ls_workorder.total
        shiny_workorder.item_description = self.item_description
        shiny_workorder.status = self.status
        try:
            shiny_workorder.customer = ShinyCustomer.objects.get(ls_customer_id=self.customer_id)
        except ShinyCustomer.DoesNotExist:
            shiny_workorder.customer = ShinyCustomer.objects.get(ls_customer_id=5896)

        return shiny_workorder, None
