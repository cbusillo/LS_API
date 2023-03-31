"""Class to import workorder objects from LS API"""
from dataclasses import dataclass
from shiny_api.classes.ls_client import Client
from shiny_api.classes.ls_customer import Customer


@dataclass
class Workorder:
    """Workorder object from LS"""
    client = Client()

    def __init__(self, workorder_id: int):
        """Workorder object from dict"""
        self.workorder_id = workorder_id
        ls_workorder = self.client.get_workorder_json(workorder_id)
        if not ls_workorder:
            return
        self.system_sku = int(ls_workorder.get("systemSku"))
        self.time_in = str(ls_workorder.get("timeIn"))
        self.eta_out = str(ls_workorder.get("etaOut"))
        self.note = str(ls_workorder.get("note"))
        self.warranty = str(ls_workorder.get("warranty"))
        self.tax = str(ls_workorder.get("tax"))
        self.archived = str(ls_workorder.get("archived"))
        self.time_stamp = str(ls_workorder.get("timeStamp"))
        self.customer_id = int(ls_workorder.get("customerID"))
        self.serialized_id = int(ls_workorder.get("serializedID"))
        self.sale_id = int(ls_workorder.get("saleID"))
        self.sale_line_id = int(ls_workorder.get("saleLineID"))
        self.item_description = str(ls_workorder.get("Serialized").get("description")).strip()
        self.total = float(ls_workorder.get("m").get("total"))
        self.customer = Customer(self.customer_id)
