"""Shiny Customer class."""
import logging
import re
from collections.abc import Iterable
from django.db import models
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict
from shiny_app.django_server.ls_functions.views import send_message
from shiny_app.classes.ls_customer import Customer as LSCustomer


class Customer(models.Model):
    """Customer object from LS"""

    ls_customer_id = models.IntegerField(null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=10, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    update_from_ls_time = models.DateTimeField(null=True)
    archived = models.BooleanField()
    contact_id = models.IntegerField()
    credit_account_id = models.IntegerField(blank=True, null=True)
    customer_type_id = models.IntegerField()
    tax_category_id = models.IntegerField(blank=True, null=True)
    is_modified = models.BooleanField(default=False)
    phones: QuerySet["Phone"]
    emails: QuerySet["Email"]
    customer: QuerySet["Customer"]

    def save(self, *args, **kwargs):
        """Save customer"""
        self.first_name = self.first_name.strip()
        self.last_name = self.last_name.strip()
        if self.title:
            self.title = self.title.strip()
        if self.company:
            self.company = self.company.strip()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        """Return string of full name"""
        return f"{self.first_name} {self.last_name}"


class Email(models.Model):
    """Contact email from dict"""

    address = models.EmailField()
    address_type = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="emails")

    class Meta:
        unique_together = ("address", "customer", "address_type")


class Phone(models.Model):
    """Contact phone"""

    number = models.CharField(max_length=20)
    number_type = models.CharField(max_length=20)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="phones")

    class Meta:
        unique_together = ("number", "customer", "number_type")


def format_customer_phone():
    """Load and iterate through customers, updating formatting on phone numbers."""
    customers = Customer.objects.all()
    if not isinstance(customers, Iterable):
        customers = [customers]
    logging.info("Updating customers")
    send_message("Updating customers")
    customers_updated = 0
    for index, customer in enumerate(customers):
        if customer.phones.count == 0:
            continue
        has_mobile = False
        phone_dict = {}
        duplicates_to_remove = []
        for each_number in customer.phones.all():
            cleaned_number = re.sub(r"[^0-9x]", "", each_number.number)

            if each_number.number != cleaned_number:
                each_number.number = cleaned_number
                customer.is_modified = True
            if len(each_number.number) == 7:
                each_number.number = f"757{cleaned_number}"
                customer.is_modified = True
            if len(each_number.number) == 11:
                each_number.number = cleaned_number[1:]
                customer.is_modified = True
            if each_number.number_type == "Mobile":
                has_mobile = True

            # Deduplicate phone numbers, prioritizing "Mobile" type
            if each_number.number not in phone_dict:
                phone_dict[each_number.number] = each_number
            else:
                if each_number.number_type == "Mobile":
                    duplicates_to_remove.append(phone_dict[each_number.number])
                    phone_dict[each_number.number] = each_number
                else:
                    duplicates_to_remove.append(each_number)

        if customer.is_modified or duplicates_to_remove or (has_mobile is False and len(phone_dict) > 0):
            # Delete duplicate phone instances causing constraint issues
            for duplicate in duplicates_to_remove:
                duplicate.delete()

            customers_updated += 1
            output = f"{customers_updated}: Updating Customer #{index}"
            send_message(output)
            logging.info(output)
            ls_customer = LSCustomer(**customer_to_dict(customer))
            ls_customer.update_phones()
            customer.is_modified = False
            customer.save()

    send_message("Finished updating customers")


def customer_to_dict(customer):
    """Convert customer to dict"""
    customer_dict = model_to_dict(customer, exclude=["phones", "emails"])
    customer_dict["customer_id"] = customer.ls_customer_id
    phones = []
    for phone in customer.phones.all():
        phones.append(model_to_dict(phone))
    customer_dict["phones"] = phones

    emails = []
    for email in customer.emails.all():
        emails.append(model_to_dict(email))
    customer_dict["emails"] = emails

    return customer_dict
