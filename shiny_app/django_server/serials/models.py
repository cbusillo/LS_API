"""Shiny Customer class."""
from django.db import models


class Serial(models.Model):
    """Customer object from LS"""

    ls_serial_id = models.IntegerField(null=True)
    value_1 = models.CharField(max_length=255, null=True)
    value_2 = models.CharField(max_length=255, null=True)
    serial_number = models.CharField(max_length=20, null=True)
    description = models.CharField(max_length=255, null=True)
    item_id = models.ForeignKey("items.Item", on_delete=models.CASCADE, null=True, related_name="serials")
    customer_id = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, null=True, related_name="serials")
