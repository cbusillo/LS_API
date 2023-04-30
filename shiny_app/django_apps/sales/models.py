"""Shiny Sales class."""
from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from ..customers.models import Customer


class SaleLine(models.Model):
    """SaleLine model."""

    ls_sale_line_id = models.IntegerField(null=True, db_index=True, unique=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    update_from_ls_time = models.DateTimeField(null=True, db_index=True)
    unit_quantity = models.IntegerField(null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount_percent = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    average_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax = models.BooleanField(null=True)
    tax_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    is_work_order = models.BooleanField(null=True)
    note = models.TextField(blank=True, null=True)
    item = models.ForeignKey("items.Item", on_delete=models.PROTECT, null=True, related_name="sale_lines")
    sale = models.ForeignKey("Sale", on_delete=models.PROTECT, null=True, related_name="sale_lines")


class Sale(models.Model):
    """Sale model."""

    ls_sale_id = models.IntegerField(null=True, db_index=True, unique=True)
    completed_time = models.DateTimeField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    update_from_ls_time = models.DateTimeField(null=True, db_index=True)
    completed = models.BooleanField(null=True)
    archived = models.BooleanField(null=True)
    voided = models.BooleanField(null=True)
    tax_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    customer: "Customer | models.ForeignKey" = models.ForeignKey(
        "customers.Customer", on_delete=models.PROTECT, null=True, related_name="sales"
    )

    sale_lines: models.QuerySet[SaleLine]
    note = models.TextField(blank=True, null=True)
