"""Class to import workorder objects from LS API"""
from datetime import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional, Self, TYPE_CHECKING
from shiny_app.classes.ls_client import BaseLSEntity

if TYPE_CHECKING:
    from shiny_app.django_server.workorders.models import (
        Workorder as ShinyWorkorder,
        WorkorderItem as ShinyWorkorderItem,
        WorkorderLine as ShinyWorkorderLine,
    )


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


@dataclass
class WorkorderItem(BaseLSEntity):
    """WorkorderItem"""

    default_params = {"load_relations": '["Discount"]'}

    workorder_item_id: int
    unit_price: Decimal
    unit_quantity: int
    tax: bool
    note: str
    workorder_id: int
    sale_line_id: int
    item_id: int
    discount_amount: Decimal
    discount_percent: Decimal
    time_stamp: datetime

    def __init__(self, *args, **kwargs):
        """WorkorderItem object from dict"""
        super().__init__()
        self.__dict__.update(kwargs)

        if self.workorder_item_id and self.fetch_from_api:
            workorder_item_json = next(self.get_entities_json(entity_id=self.workorder_item_id))
            workorder_item = self.from_json(workorder_item_json)
            self.__dict__.update(workorder_item.__dict__)

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> Self:
        """WorkorderItem object from dict"""

        if not isinstance(json, dict):
            raise ValueError("WorkorderItem must be a dict: " + str(json))

        workorder_item_json_transformed = {
            "workorder_item_id": cls.safe_int(json.get("workorderItemID")),
            "unit_price": Decimal(json.get("unitPrice", 0)),
            "unit_quantity": cls.safe_int(json.get("unitQuantity")),
            "tax": json.get("tax", "").lower() == "true",
            "note": json.get("note"),
            "workorder_id": cls.safe_int(json.get("workorderID")),
            "sale_line_id": cls.safe_int(json.get("saleLineID")),
            "item_id": cls.safe_int(json.get("itemID")),
            "discount_amount": Decimal(json.get("Discount", {}).get("amount", 0)),
            "discount_percent": Decimal(json.get("Discount", {}).get("percent", 0)),
            "time_stamp": cls.string_to_datetime(json.get("timeStamp")),
        }
        return cls(**workorder_item_json_transformed)

    def shiny_workorder_item_from_ls(self, shiny_workorder_item: "ShinyWorkorderItem", start_time: datetime):
        """Convert LS WorkorderItem to Shiny WorkorderItem"""
        # pylint: disable=import-outside-toplevel
        from shiny_app.django_server.workorders.models import Workorder as ShinyWorkorder
        from shiny_app.django_server.items.models import Item as ShinyItem

        shiny_workorder_item.ls_workorder_item_id = self.workorder_item_id
        shiny_workorder_item.unit_price = self.unit_price
        shiny_workorder_item.unit_quantity = self.unit_quantity
        shiny_workorder_item.tax = self.tax
        shiny_workorder_item.note = self.note
        shiny_workorder_item.update_time = start_time
        shiny_workorder_item.update_from_ls_time = start_time
        shiny_workorder_item.discount_amount = self.discount_amount
        shiny_workorder_item.discount_percent = self.discount_percent
        shiny_workorder_item.item = ShinyItem.objects.get(ls_item_id=self.item_id)
        # shiny_workorder_item.sale_line_id = self.sale_line_id
        shiny_workorder_item.workorder = ShinyWorkorder.objects.get(ls_workorder_id=self.workorder_id)

        return shiny_workorder_item, None


@dataclass
class WorkorderLine(BaseLSEntity):
    """WorkorderLine"""

    default_params = {"load_relations": '["Discount"]'}

    workorder_line_id: int
    note: str
    time_stamp: datetime
    unit_price: Decimal
    unit_quantity: int
    unit_cost: Decimal
    tax: bool
    workorder_id: int
    # sale_line_id: int
    discount_amount: Decimal
    discount_percent: Decimal

    def __init__(self, *args, **kwargs):
        """WorkorderLine object from dict"""
        super().__init__()
        self.__dict__.update(kwargs)

        if self.workorder_line_id and self.fetch_from_api:
            workorder_line_json = next(self.get_entities_json(entity_id=self.workorder_line_id))
            workorder_line = self.from_json(workorder_line_json)
            self.__dict__.update(workorder_line.__dict__)

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> Self:
        """WorkorderLine object from dict"""

        if not isinstance(json, dict):
            raise ValueError("WorkorderLine must be a dict: " + str(json))

        workorder_line_json_transformed = {
            "workorder_line_id": cls.safe_int(json.get("workorderLineID")),
            "note": json.get("note"),
            "time_stamp": cls.string_to_datetime(json.get("timeStamp")),
            "unit_price": Decimal(json.get("unitPrice", 0)),
            "unit_quantity": cls.safe_int(json.get("unitQuantity")),
            "unit_cost": Decimal(json.get("unitCost", 0)),
            "tax": json.get("tax", "").lower() == "true",
            "workorder_id": cls.safe_int(json.get("workorderID")),
            # "sale_line_id": cls.safe_int(json.get("saleLineID")),
            "discount_amount": Decimal(json.get("Discount", {}).get("discountAmount", 0)),
            "discount_percent": Decimal(json.get("Discount", {}).get("discountPercent", 0)),
        }
        return cls(**workorder_line_json_transformed)

    def shiny_workorder_line_from_ls(self, shiny_workorder_line: "ShinyWorkorderLine", start_time: datetime):
        """Convert LS WorkorderLine to Shiny WorkorderLine"""
        # pylint: disable=import-outside-toplevel
        from shiny_app.django_server.workorders.models import Workorder as ShinyWorkorder

        shiny_workorder_line.ls_workorder_line_id = self.workorder_line_id
        shiny_workorder_line.note = self.note
        shiny_workorder_line.update_time = start_time
        shiny_workorder_line.update_from_ls_time = start_time
        shiny_workorder_line.unit_price = self.unit_price
        shiny_workorder_line.unit_quantity = self.unit_quantity
        shiny_workorder_line.unit_cost = self.unit_cost
        shiny_workorder_line.tax = self.tax
        shiny_workorder_line.discount_amount = self.discount_amount
        shiny_workorder_line.discount_percent = self.discount_percent
        shiny_workorder_line.workorder = ShinyWorkorder.objects.get(ls_workorder_id=self.workorder_id)

        return shiny_workorder_line, None
