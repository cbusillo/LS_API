"""Shiny Workorder class."""
from django.db import models
from shiny_app.modules.label_print import print_text
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
    # total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.customer.full_name} - {self.status} - {self.time_in}"

    def print_label(self, quantity: int = 1) -> None:
        """Print a label for this workorder."""
        password = ""
        note_string = str(self.note)
        for line in note_string.split("\n"):
            if line[0:2].lower() == "pw" or line[0:2].lower() == "pc":
                password = line
        print_text(
            f"{self.customer.full_name}",
            barcode=f"2500000{self.ls_workorder_id}",
            quantity=quantity,
            text_bottom=password,
            print_date=True,
        )
