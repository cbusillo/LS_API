"""Shiny Item class."""
from typing import TYPE_CHECKING
from django.db import models
from django.db.models.query import QuerySet

if TYPE_CHECKING:
    from ..customers.models import Customer


class Item(models.Model):
    """Item model."""

    ls_item_id = models.IntegerField(null=True, db_index=True, unique=True)
    default_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    average_cost = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax = models.BooleanField(null=True)
    archived = models.BooleanField(null=True)
    item_type = models.CharField(max_length=20, null=True)
    serialized = models.BooleanField(null=True)
    description = models.CharField(max_length=255)
    model_year = models.IntegerField(null=True)
    upc = models.CharField(max_length=20, blank=True, null=True)
    custom_sku = models.CharField(max_length=20, blank=True, null=True)
    manufacturer_sku = models.CharField(max_length=20, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    update_from_ls_time = models.DateTimeField(null=True, db_index=True)
    item_matrix_id = models.IntegerField(null=True)
    sizes = models.TextField(max_length=300, null=True)
    serials = QuerySet["Serial"]

    def __str__(self) -> str:
        return f"{self.ls_item_id} - {self.description}"


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
