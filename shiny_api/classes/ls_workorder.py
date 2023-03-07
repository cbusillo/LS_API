"""Class to import workorder objects from LS API"""
import os
from dataclasses import dataclass
from shiny_api.modules.connect_ls import generate_ls_access, get_data
from shiny_api.modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")


@dataclass
class Workorder:
    """Workorder object from LS"""

    def __init__(self, workorder_id: int):
        """Workorder object from dict"""
        self.workorder_id = workorder_id
        ls_workorder = self._get_workorder()

        self.system_sku = int(ls_workorder.get("systemSku"))
        self.time_in = str(ls_workorder.get("timeIn"))
        self.eta_out = str(ls_workorder.get("etaOut"))
        self.note = str(ls_workorder.get("note"))
        self.warranty = str(ls_workorder.get("warranty"))
        self.tax = str(ls_workorder.get("tax"))
        self.archived = str(ls_workorder.get("archived"))
        self.hook_in = str(ls_workorder.get("hookIn"))
        self.hook_out = str(ls_workorder.get("hookOut"))
        self.save_parts = str(ls_workorder.get("saveParts"))
        self.assign_employee_to_all = str(ls_workorder.get("assignEmployeeToAll"))
        self.time_stamp = str(ls_workorder.get("timeStamp"))
        self.customer_id = int(ls_workorder.get("customerID"))
        self.discount_id = int(ls_workorder.get("discountID"))
        self.employee_id = int(ls_workorder.get("employeeID"))
        self.serialized_id = int(ls_workorder.get("serializedID"))
        self.shop_id = int(ls_workorder.get("shopID"))
        self.sale_id = int(ls_workorder.get("saleID"))
        self.sale_line_id = int(ls_workorder.get("saleLineID"))
        self.item_description = str(ls_workorder.get("Serialized").get("description")).strip()
        self.total = float(ls_workorder.get("m").get("total"))

    def _get_workorder(self):
        """Get single workorder from LS API into workorder object"""
        generate_ls_access()
        response = get_data(config.LS_URLS["workorder"].format(workorderID=self.workorder_id))
        return response.json().get("Workorder")
