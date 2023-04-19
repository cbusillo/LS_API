"""Serial class from LS"""
import logging
from typing import Any, Optional, Self, TYPE_CHECKING
from datetime import datetime
from dataclasses import dataclass
from shiny_app.classes.ls_client import BaseLSEntity

if TYPE_CHECKING:
    from shiny_app.django_server.serials.models import Serial as ShinySerial


@dataclass
class Serialized(BaseLSEntity):
    """Serial class from LS"""

    class_params = {}

    serial_id: Optional[int] = None
    value_1: Optional[str] = None
    value_2: Optional[str] = None
    serial_number: Optional[str] = None
    description: Optional[str] = None
    item_id: Optional[int] = None
    customer_id: Optional[int] = None
    time_stamp: Optional[datetime] = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)

        if self.serial_id and self.fetch_from_api:
            serial_json = next(self.get_entities_json(entity_id=self.serial_id))
            serial = self.from_json(serial_json)
            self.__dict__.update(serial.__dict__)

    @classmethod
    def from_json(cls, data_json: dict[str, Any]) -> Self:
        if not isinstance(data_json, dict):
            raise TypeError("serial_json must be a dict")

        serial_json_transformed = {
            "serial_id": cls.safe_int(data_json.get("serializedID")),
            "value_1": data_json.get("colorName"),
            "value_2": data_json.get("sizeName"),
            "serial_number": data_json.get("serial"),
            "description": data_json.get("description"),
            "item_id": cls.safe_int(data_json.get("itemID")),
            "customer_id": cls.safe_int(data_json.get("customerID")),
            "time_stamp": cls.string_to_datetime(data_json.get("timeStamp")),
        }

        return cls(**serial_json_transformed)

    def shiny_serial_from_ls(self, shiny_serial: "ShinySerial", start_time: datetime):
        """translation layer for LSSerial to ShinySerial"""
        # pylint: disable=import-outside-toplevel
        from shiny_app.django_server.customers.models import Customer as ShinyCustomer
        from shiny_app.django_server.items.models import Item as ShinyItem

        shiny_serial.ls_serial_id = self.serial_id
        shiny_serial.value_1 = self.value_1
        shiny_serial.value_2 = self.value_2
        shiny_serial.serial_number = self.serial_number
        shiny_serial.description = self.description
        shiny_serial.create_time = self.time_stamp or start_time
        shiny_serial.update_time = start_time
        shiny_serial.update_from_ls_time = start_time

        if self.customer_id:
            try:
                shiny_serial.customer = ShinyCustomer.objects.get(ls_customer_id=self.customer_id)
            except ShinyCustomer.DoesNotExist:
                shiny_serial.customer = ShinyCustomer.objects.get(ls_customer_id=5896)

        if self.item_id:
            try:
                shiny_serial.item = ShinyItem.objects.get(ls_item_id=self.item_id)
            except ShinyItem.DoesNotExist:
                logging.error("Item %i not found in ShinyItem", self.item_id)

        return shiny_serial, None
