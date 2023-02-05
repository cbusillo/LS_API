"""Class to import workorder objects from LS API"""
import os
import json
from datetime import datetime
from typing import Any
from dataclasses import dataclass
from shiny_api.modules.connect_ls import generate_ls_access, get_data
from shiny_api.modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")


def to_json(tojson):
    """convert string to JSON"""
    return json.dumps(
        tojson,
        default=lambda o: o.__dict__,
        sort_keys=True,
        indent=None,
        separators=(", ", ": "),
    )


@dataclass
class Workorder:
    """Workorder object from LS"""

    workorder_id: int
    system_sku: str
    time_in: datetime
    eta_out: datetime
    note: str
    warranty: bool
    tax: bool
    archived: bool
    hook_in: str
    hook_out: str
    save_parts: bool
    assign_employee_to_all: bool
    time_stamp: datetime
    customer_id: int
    discount_id: int
    employee_id: int
    serialized_id: int
    shop_id: int
    sale_id: int
    sale_line_id: int

    @staticmethod
    def from_dict(obj: Any) -> "Workorder":
        """Workorder object from dict"""
        _workorder_id = str(obj.get("workorderID"))
        _system_sku = str(obj.get("systemSku"))
        _time_in = str(obj.get("timeIn"))
        _eta_out = str(obj.get("etaOut"))
        _note = str(obj.get("note"))
        _warranty = str(obj.get("warranty"))
        _tax = str(obj.get("tax"))
        _archived = str(obj.get("archived"))
        _hook_in = str(obj.get("hookIn"))
        _hook_out = str(obj.get("hookOut"))
        _save_parts = str(obj.get("saveParts"))
        _assign_employee_to_all = str(obj.get("assignEmployeeToAll"))
        _time_stamp = str(obj.get("timeStamp"))
        _customer_id = str(obj.get("customerID"))
        _discount_id = str(obj.get("discountID"))
        _employee_id = str(obj.get("employeeID"))
        _serialized_id = str(obj.get("serializedID"))
        _shop_id = str(obj.get("shopID"))
        _sale_id = str(obj.get("saleID"))
        _sale_line_id = str(obj.get("saleLineID"))
        return Workorder(
            _workorder_id,
            _system_sku,
            _time_in,
            _eta_out,
            _note,
            _warranty,
            _tax,
            _archived,
            _hook_in,
            _hook_out,
            _save_parts,
            _assign_employee_to_all,
            _time_stamp,
            _customer_id,
            _discount_id,
            _employee_id,
            _serialized_id,
            _shop_id,
            _sale_id,
            _sale_line_id,
        )

    @staticmethod
    def get_workorder(workorder_id):
        """Get single workorder from LS API into workorder object"""
        generate_ls_access()
        response = get_data(config.LS_URLS["workorderSingle"].format(workorderID=workorder_id))

        return Workorder.from_dict(response.json().get("Workorder"))
