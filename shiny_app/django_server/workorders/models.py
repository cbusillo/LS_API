"""Shiny Workorder class."""
from django.db import models

from shiny_app.classes.config import Config
from shiny_app.modules.label_print import print_text
from shiny_app.modules.ring_central import send_message_ssh as send_message


class WorkorderItem(models.Model):
    """WorkorderItem Shiny Object"""

    ls_workorder_item_id = models.IntegerField(null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    unit_quantity = models.IntegerField(null=True)
    tax = models.BooleanField(null=True)
    note = models.TextField(blank=True, null=True)
    workorder = models.ForeignKey("Workorder", on_delete=models.CASCADE, related_name="workorder_items")
    # sale_line
    item = models.ForeignKey("items.Item", on_delete=models.PROTECT, related_name="workorder_items")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    update_from_ls_time = models.DateTimeField(null=True)


class WorkorderLine(models.Model):
    """WorkorderLine Shiny Object"""

    ls_workorder_line_id = models.IntegerField(null=True)
    note = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    update_from_ls_time = models.DateTimeField(null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    unit_quantity = models.IntegerField(null=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax = models.BooleanField(null=True)
    workorder = models.ForeignKey("Workorder", on_delete=models.CASCADE, related_name="workorder_lines")
    # sale_line_id: int
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True)


class Workorder(models.Model):
    """Workorder Shiny Object"""

    ls_workorder_id = models.IntegerField(null=True)
    time_in = models.DateTimeField(null=True)
    eta_out = models.DateTimeField(null=True)
    note = models.TextField(blank=True, null=True)
    warranty = models.BooleanField(null=True)
    tax = models.BooleanField(null=True)
    archived = models.BooleanField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    update_from_ls_time = models.DateTimeField(null=True)
    item_description = models.CharField(max_length=100, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    status = models.CharField(max_length=20, null=True)
    customer = models.ForeignKey("customers.Customer", on_delete=models.PROTECT, related_name="workorders_related")
    workorder_items: models.QuerySet[WorkorderItem]

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

    def send_rc_message(self, message_number: int, ip_address: str) -> None:
        """Send a message to the customer via RingCentral."""

        # if workorder.total == 0 and request.GET.get("message") == "2":  # if we send a message with price with $0 price
        #     message_number += 1
        item_description = str(self.item_description)
        if item_description:
            for word in Config.STYLIZED_NAMES:
                if word.lower() in item_description.lower() and word not in item_description:
                    index = item_description.lower().find(word.lower())
                    item_description = item_description[:index] + word + item_description[index + len(word) :]

        message = Config.RESPONSE_MESSAGES[message_number]
        message = message.format(
            name=self.customer.first_name,
            product=item_description,
            # total=locale.currency(workorder.total),
        )
        mobile_number = self.customer.mobile_number
        if mobile_number:
            send_message(mobile_number, message, ip_address)
