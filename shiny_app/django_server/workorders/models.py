"""Shiny Workorder class."""
from django.db import models
from ..customers.models import Customer


class Workorder(models.Model):
    """Workorder Shiny Object"""

    ls_workorder_id = models.IntegerField(null=True)
    time_in = models.DateTimeField(null=True)
    eta_out = models.DateTimeField(null=True)
    note = models.TextField(blank=True, null=True)
    warranty = models.BooleanField()
    tax = models.BooleanField()
    archived = models.BooleanField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    update_from_ls_time = models.DateTimeField(null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.customer.full_name} - {self.status} - {self.time_in}"
