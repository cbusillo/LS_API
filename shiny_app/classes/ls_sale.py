"""Class to import sale objects from LS API"""
from datetime import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional, Self, TYPE_CHECKING
from shiny_app.classes.ls_client import BaseLSEntity

if TYPE_CHECKING:
    from shiny_app.django_apps.sales.models import (
        Sale as ShinySale,
        SaleLine as ShinySaleLine,
    )


@dataclass
class Sale(BaseLSEntity):
    """Sale object from LS"""

    class_params = {"load_relations": '["Discount","SaleNotes"]'}

    sale_id: Optional[int] = None
    time_stamp: Optional[datetime] = None
    completed: Optional[bool] = None
    archived: Optional[bool] = None
    voided: Optional[bool] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    tax_rate: Optional[Decimal] = None
    is_work_order: Optional[bool] = None
    note: Optional[str] = None
    customer_id: Optional[int] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

        sale_json_transformed = {"": ""}

        return cls(**sale_json_transformed)
