"""Shiny Customer class."""
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


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

    def save(self, *args, **kwargs):
        """Save customer"""
        self.first_name = self.first_name.strip()
        self.last_name = self.last_name.strip()
        if self.title:
            self.title = self.title.strip()
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
    use_type = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="emails")


class Phone(models.Model):
    """Contact phone"""

    number = PhoneNumberField(blank=True)
    use_type = models.CharField(max_length=20)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="phones")
