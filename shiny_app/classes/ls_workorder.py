"""Class to import workorder objects from LS API"""
from datetime import datetime
from dataclasses import dataclass
from typing import Any
from shiny_api.classes.ls_client import Client


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
        self.time_in = str(ls_workorder.get("timeIn"))
        self.eta_out = str(ls_workorder.get("etaOut"))
        self.note = str(ls_workorder.get("note"))
        self.warranty = ls_workorder.get("warranty").lower() == "true"
        self.tax = ls_workorder.get("tax").lower() == "true"
        self.archived = ls_workorder.get("archived").lower() == "true"
        self.time_stamp = str(ls_workorder.get("timeStamp"))
        self.customer_id = int(ls_workorder.get("customerID"))
        self.serialized_id = int(ls_workorder.get("serializedID"))
        self.sale_id = int(ls_workorder.get("saleID"))
        self.sale_line_id = int(ls_workorder.get("saleLineID"))
        serialized = ls_workorder.get("Serialized")
        if serialized:
            self.item_description = serialized.get("description").strip()
        self.total = float(ls_workorder.get("m").get("total"))
        workorder_status = ls_workorder.get("WorkorderStatus")
        if workorder_status:
            self.status = str(workorder_status.get("name"))
        # self.customer = Customer(self.customer_id)

    @classmethod
    def get_workorders(cls, workorder_id: int = 0, date_filter: datetime | None = None):
        """Run API auth."""
        if workorder_id != 0:
            yield Workorder(workorder_id=workorder_id)
            return
        for workorder in cls.client.get_workorders_json(date_filter=date_filter):
            yield Workorder(ls_workorder=workorder)
