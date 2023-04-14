"""Class to import workorder objects from LS API"""
from datetime import datetime
from dataclasses import dataclass
from typing import Any, Generator
from shiny_app.classes.ls_client import Client, string_to_datetime


@dataclass
class Workorder:
    """Workorder object from LS"""

    client = Client()

    def __init__(self, workorder_id: int = 0, ls_workorder: Any = None):
        """Workorder object from dict"""
        if ls_workorder is None:
            if workorder_id == 0:
                raise ValueError("Must provide workorder_id or ls_workorder")
            ls_workorder = self.client.get_workorder_json(workorder_id)
        if ls_workorder is None:
            self.workorder_id = 0
            return

        if not ls_workorder:
            return
        self.workorder_id = int(ls_workorder.get("workorderID"))
        self.system_sku = int(ls_workorder.get("systemSku"))
        self.time_in = None if (time_in := ls_workorder.get("timeIn")) is None else string_to_datetime(time_in)
        self.eta_out = None if (eta_out := ls_workorder.get("etaOut")) is None else string_to_datetime(eta_out)
        self.note = ls_workorder.get("note") or ""
        self.warranty = ls_workorder.get("warranty").lower() == "true"
        self.tax = ls_workorder.get("tax").lower() == "true"
        self.archived = ls_workorder.get("archived").lower() == "true"
        self.time_stamp = string_to_datetime(ls_workorder.get("timeStamp"))
        self.customer_id = int(ls_workorder.get("customerID"))
        self.serialized_id = int(ls_workorder.get("serializedID"))
        self.sale_id = int(ls_workorder.get("saleID"))
        self.sale_line_id = int(ls_workorder.get("saleLineID"))
        self.item_description = (
            None if (serialized := ls_workorder.get("Serialized")) is None else serialized.get("description").strip() or None
        )
        self.status = (
            None if (workorder_status := ls_workorder.get("WorkorderStatus")) is None else workorder_status.get("name") or None
        )

    @classmethod
    def get_workorders(cls, workorder_id: int = 0, date_filter: datetime | None = None) -> Generator["Workorder", None, None]:
        """Run API auth."""
        if workorder_id != 0:
            yield Workorder(workorder_id=workorder_id)
            return
        for workorder in cls.client.get_workorders_json(date_filter=date_filter):
            yield Workorder(ls_workorder=workorder)
