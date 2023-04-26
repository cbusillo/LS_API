"""Shiny Customer class."""
from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from ..customers.models import Customer
    from ..items.models import Item


class Serial(models.Model):
    """Customer object from LS"""

    ls_serial_id = models.IntegerField(null=True, db_index=True, unique=True)
    value_1 = models.CharField(max_length=255, null=True)
    value_2 = models.CharField(max_length=255, null=True)
    serial_number = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=255, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    update_from_ls_time = models.DateTimeField(null=True, db_index=True)
    item: "Item | models.ForeignKey" = models.ForeignKey("items.Item", on_delete=models.PROTECT, null=True, related_name="serials")
    customer: "Customer | models.ForeignKey" = models.ForeignKey(
        "customers.Customer", on_delete=models.PROTECT, null=True, related_name="serials"
    )
