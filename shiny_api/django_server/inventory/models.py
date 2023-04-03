"""Shiny Item class."""
from django.db import models


class ItemAttributeSet(models.Model):
    """Item Attribute Set model. This containts the type of the attributes."""

    item_attribute_set_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    attribute_name1 = models.CharField(max_length=255, blank=True)
    attribute_name2 = models.CharField(max_length=255, blank=True)
    attribute_name3 = models.CharField(max_length=255, blank=True)
    system = models.BooleanField()
    archived = models.BooleanField()


class ItemAttributes(models.Model):
    """Represents the attributes of an item."""

    attribute1 = models.CharField(max_length=255, blank=True)
    attribute2 = models.CharField(max_length=255, blank=True)
    attribute3 = models.CharField(max_length=255, blank=True)
    item_attribute_set = models.ForeignKey(ItemAttributeSet, on_delete=models.CASCADE)


class Item(models.Model):
    """Item model."""

    ls_item_id = models.IntegerField(primary_key=True)
    default_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    average_cost = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    tax = models.BooleanField()
    archived = models.BooleanField()
    item_type = models.CharField(max_length=20)
    serialized = models.BooleanField()
    description = models.CharField(max_length=255)
    model_year = models.IntegerField(null=True)
    upc = models.CharField(max_length=12, blank=True)
    custom_sku = models.CharField(max_length=20, blank=True)
    manufacturer_sku = models.CharField(max_length=20)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    updated_from_ls_time = models.DateTimeField(null=True)
    item_matrix_id = models.IntegerField()
    item_attributes = models.ForeignKey(
        ItemAttributes, on_delete=models.CASCADE, null=True
    )

    def __str__(self) -> str:
        return f"{self.ls_item_id} - {self.description}"
