"""Shiny Customer class."""
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Email(models.Model):
    """Contact email from dict"""

    address = models.EmailField()
    use_type = models.CharField(max_length=100)


class Phone(models.Model):
    """Contact phone"""

    number = PhoneNumberField(blank=True)
    use_type = models.CharField(max_length=20)


class Customer(models.Model):
    """Customer object from LS"""

    ls_customer_id = models.IntegerField(null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=10, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    updated_from_ls_time = models.DateTimeField(null=True)
    archived = models.BooleanField()
    contact_id = models.IntegerField()
    credit_account_id = models.IntegerField(blank=True, null=True)
    customer_type_id = models.IntegerField()
    discount_id = models.IntegerField(blank=True, null=True)
    tax_category_id = models.IntegerField(blank=True, null=True)
    is_modified = models.BooleanField(default=False)
    emails = models.ManyToManyField(Email, blank=True)
    phones = models.ManyToManyField(Phone, blank=True)
