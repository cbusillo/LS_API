"""Shiny Item class."""
from typing import TYPE_CHECKING
from django.db import models
from django.db.models.query import QuerySet

if TYPE_CHECKING:
    from ..serials.models import Serial


class ItemAttributes(models.Model):
    """Represents the attributes of an item."""

    attribute1 = models.CharField(max_length=255, blank=True)
    attribute2 = models.CharField(max_length=255, blank=True)
    attribute3 = models.CharField(max_length=255, blank=True)
    item_attribute_id = models.IntegerField()


class Item(models.Model):
    """Item model."""

    ls_item_id = models.IntegerField(null=True)
    default_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    average_cost = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax = models.BooleanField(null=True)
    archived = models.BooleanField(null=True)
    item_type = models.CharField(max_length=20, null=True)
    serialized = models.BooleanField(null=True)
    description = models.CharField(max_length=255)
    model_year = models.IntegerField(null=True)
    upc = models.CharField(max_length=12, blank=True, null=True)
    custom_sku = models.CharField(max_length=20, blank=True, null=True)
    manufacturer_sku = models.CharField(max_length=20, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    update_from_ls_time = models.DateTimeField(null=True)
    item_matrix_id = models.IntegerField(null=True)
    item_attributes = models.ForeignKey(ItemAttributes, on_delete=models.CASCADE, null=True)
    sizes = models.CharField(max_length=200, null=True)
    serials = QuerySet["Serial"]

    def __str__(self) -> str:
        return f"{self.ls_item_id} - {self.description}"
