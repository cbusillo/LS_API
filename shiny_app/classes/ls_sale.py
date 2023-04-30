"""Class to import sale objects from LS API"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional, Self

from shiny_app.classes.ls_client import BaseLSEntity
from shiny_app.django_apps.sales.models import Sale as ShinySale
from shiny_app.django_apps.sales.models import SaleLine as ShinySaleLine


@dataclass
class Sale(BaseLSEntity):
    """Sale object from LS"""

    class_params = {"load_relations": '["Discount","SaleNotes"]'}

    sale_id: Optional[int] = None
    time_stamp: Optional[datetime] = None
    completed: Optional[bool] = None
    completed_time: Optional[datetime] = None
    archived: Optional[bool] = None
    voided: Optional[bool] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    tax_rate: Optional[Decimal] = None
    is_work_order: Optional[bool] = None
    note: Optional[str] = None
    customer_id: Optional[int] = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)

        if self.sale_id and self.fetch_from_api:
            sale_json = next(self.get_entities_json(entity_id=self.sale_id))
            sale = self.from_json(sale_json)
            self.__dict__.update(sale.__dict__)

    @classmethod
    def from_json(cls, data_json: dict[str, Any]) -> Self:
        """Sale object from dict"""

        if not isinstance(data_json, dict):
            raise TypeError("data_json must be a dict")

        sale_json_transformed = {
            "sale_id": data_json.get("saleID"),
            "time_stamp": cls.string_to_datetime(data_json.get("timeStamp")),
            "completed": data_json.get("completed", "").lower() == "true",
            "completed_time": cls.string_to_datetime(data_json.get("completedTime")),
            "archived": data_json.get("archived", "").lower() == "true",
            "voided": data_json.get("voided", "").lower() == "true",
            "tax_rate": Decimal(data_json.get("taxRate", 0)),
            "customer_id": data_json.get("customerID"),
            "note": data_json.get("Note"),
        }

        return cls(**sale_json_transformed)

    def shiny_sale_from_ls(self, shiny_sale: "ShinySale", start_time: datetime):
        """Update shiny sale from LS sale"""
        from shiny_app.django_apps.customers.models import Customer as ShinyCustomer  # pylint: disable=import-outside-toplevel

        shiny_sale.ls_sale_id = self.sale_id
        shiny_sale.completed_time = self.completed_time
        shiny_sale.create_time = self.time_stamp or start_time
        shiny_sale.update_time = self.update_time or start_time
        shiny_sale.update_from_ls_time = start_time
        shiny_sale.completed = self.completed
        shiny_sale.archived = self.archived
        shiny_sale.voided = self.voided
        shiny_sale.tax_rate = self.tax_rate
        shiny_sale.note = self.note
        try:
            shiny_sale.customer = ShinyCustomer.objects.get(ls_customer_id=self.customer_id)
        except ShinyCustomer.DoesNotExist:
            shiny_sale.customer = ShinyCustomer.objects.get(ls_customer_id=5896)

        return None


@dataclass
class SaleLine(BaseLSEntity):
    """SaleLine"""

    class_params = {"load_relations": '["Discount", "Note", "TaxClass"]'}

    sale_line_id: Optional[int] = None
    create_time: Optional[datetime] = None
    time_stamp: Optional[datetime] = None
    unit_quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    average_cost: Optional[Decimal] = None
    tax: Optional[bool] = None
    tax_rate: Optional[Decimal] = None
    is_work_order: Optional[bool] = None
    note: Optional[str] = None
    item_id: Optional[int] = None
    sale_id: Optional[int] = None
    work_order_id: Optional[int] = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)

        if self.sale_line_id and self.fetch_from_api:
            sale_line_json = next(self.get_entities_json(entity_id=self.sale_line_id))
            sale_line = self.from_json(sale_line_json)
            self.__dict__.update(sale_line.__dict__)

    @classmethod
    def from_json(cls, data_json: dict[str, Any]) -> Self:
        """SaleLine object from dict"""

        if not isinstance(data_json, dict):
            raise TypeError("SaleLine must be a dict")
        note = data_json.get("Note", {}).get("note")
        sale_line_json_transformed = {
            "sale_line_id": cls.safe_int(data_json.get("saleLineID")),
            "create_time": cls.string_to_datetime(data_json.get("createTime")),
            "time_stamp": cls.string_to_datetime(data_json.get("timeStamp")),
            "unit_quantity": cls.safe_int(data_json.get("unitQuantity")),
            "unit_price": Decimal(data_json.get("unitPrice", 0)),
            "discount_amount": Decimal(data_json.get("discountAmount", 0)),
            "discount_percent": Decimal(data_json.get("discountPercent", 0)),
            "average_cost": Decimal(data_json.get("avgCost", 0)),
            "tax": data_json.get("tax", "").lower() == "true",
            "tax_rate": Decimal(data_json.get("taxRate", 0)),
            "is_work_order": data_json.get("isWorkOrder", "").lower() == "true",
            "note": note,
            "item_id": cls.safe_int(data_json.get("itemID")),
            "sale_id": cls.safe_int(data_json.get("saleID")),
        }
        if sale_line_json_transformed["sale_id"] == 0:
            pass
        return cls(**sale_line_json_transformed)

    def shiny_sale_line_from_ls(self, shiny_sale_line: "ShinySaleLine", start_time: datetime) -> None:
        """Update shiny sale line from LS sale line"""
        from shiny_app.django_apps.items.models import Item as ShinyItem  # pylint: disable=import-outside-toplevel

        shiny_sale_line.ls_sale_line_id = self.sale_line_id
        shiny_sale_line.create_time = self.create_time or start_time
        shiny_sale_line.update_time = self.time_stamp or start_time
        shiny_sale_line.update_from_ls_time = start_time
        shiny_sale_line.unit_quantity = self.unit_quantity
        shiny_sale_line.unit_price = self.unit_price
        shiny_sale_line.discount_amount = self.discount_amount
        shiny_sale_line.discount_percent = self.discount_percent
        shiny_sale_line.average_cost = self.average_cost
        shiny_sale_line.tax = self.tax
        shiny_sale_line.tax_rate = self.tax_rate
        shiny_sale_line.is_work_order = self.is_work_order
        shiny_sale_line.note = self.note
        if self.sale_id:
            shiny_sale_line.sale = ShinySale.objects.get(ls_sale_id=self.sale_id)  # pyright: ignore[reportGeneralTypeIssues]

        try:
            shiny_sale_line.item = ShinyItem.objects.get(ls_item_id=self.item_id)  # pyright: ignore[reportGeneralTypeIssues]
        except ShinyItem.DoesNotExist:
            shiny_sale_line.item = None
        return None
