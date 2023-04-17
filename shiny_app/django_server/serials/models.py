"""Shiny Customer class."""
from django.db import models


class Serial(models.Model):
    """Customer object from LS"""

    ls_serial_id = models.IntegerField(null=True)
    value_1 = models.CharField(max_length=255, null=True)
    value_2 = models.CharField(max_length=255, null=True)
    serial_number = models.CharField(max_length=20, null=True)
    description = models.CharField(max_length=255, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    update_from_ls_time = models.DateTimeField(null=True)
    item = models.ForeignKey("items.Item", on_delete=models.PROTECT, null=True)
    customer = models.ForeignKey("customers.Customer", on_delete=models.PROTECT, null=True)
