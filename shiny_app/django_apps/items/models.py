"""Shiny Item class."""
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

if TYPE_CHECKING:
    from ..customers.models import Customer


class Item(models.Model):
    """Item model."""

    ls_item_id = models.IntegerField(null=True, db_index=True, unique=True)
    default_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    average_cost = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax = models.BooleanField(null=True)
    archived = models.BooleanField(null=True)
    item_type = models.CharField(max_length=20, null=True)
    serialized = models.BooleanField(null=True)
    description = models.CharField(max_length=255)
    model_year = models.IntegerField(null=True)
    upc = models.CharField(max_length=20, blank=True, null=True)
    custom_sku = models.CharField(max_length=20, blank=True, null=True)
    manufacturer_sku = models.CharField(max_length=20, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    update_from_ls_time = models.DateTimeField(null=True, db_index=True)
    item_matrix_id = models.IntegerField(null=True)
    sizes = models.TextField(max_length=300, null=True)
    serials = models.QuerySet["Serial"]

    def __str__(self) -> str:
        return f"{self.ls_item_id} - {self.description}"


class Serial(models.Model):
    """Customer object from LS"""

    ls_serial_id = models.IntegerField(null=True, db_index=True, unique=True)
    value_1 = models.CharField(max_length=255, null=True)
    value_2 = models.CharField(max_length=255, null=True)
    serial_number = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=255, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    update_from_ls_time = models.DateTimeField(null=True, db_index=True)
    item: "Item | models.ForeignKey" = models.ForeignKey("items.Item", on_delete=models.PROTECT, null=True, related_name="serials")
    customer: "Customer | models.ForeignKey" = models.ForeignKey(
        "customers.Customer", on_delete=models.PROTECT, null=True, related_name="serials"
    )


class DeviceCodeNameModel(models.Model):
    """Abstract model for code/name pairs."""

    code = models.CharField(max_length=5, db_index=True, unique=True)
    name = models.CharField(max_length=30)
    sort_order = models.IntegerField(default=0)

    class Meta:
        """Meta class."""

        abstract = True
        ordering = ["sort_order", "code"]

    def __str__(self) -> str:
        """Return string representation."""
        return str(self.name)

    def save(self, *args, **kwargs):
        """Override save method."""
        if self.pk:
            original = self.__class__.objects.get(pk=self.pk)
            if original.code != self.code:
                raise ValidationError("Code cannot be changed.")
        self.code = self.code.upper()
        super().save(*args, **kwargs)


class DeviceFunctionalAttribute(DeviceCodeNameModel):
    """Listing functional attribute choices."""

    pass  # pylint: disable=unnecessary-pass


class DeviceType(DeviceCodeNameModel):
    """Listing type choices."""

    pass  # pylint: disable=unnecessary-pass


class DevicePart(DeviceCodeNameModel):
    """Listing part choices."""

    pass  # pylint: disable=unnecessary-pass


class DeviceProcessorType(DeviceCodeNameModel):
    """Listing processor choices."""

    pass  # pylint: disable=unnecessary-pass


class DeviceGPU(DeviceCodeNameModel):
    """Listing GPU choices."""

    class Meta:
        verbose_name = "Device GPU"
        verbose_name_plural = "Device GPUs"


class Device(models.Model):
    """Device model."""

    device_type = models.ForeignKey(DeviceType, on_delete=models.PROTECT)
    part = models.ForeignKey(DevicePart, on_delete=models.PROTECT)
    processor_type = models.ForeignKey(DeviceProcessorType, on_delete=models.PROTECT, null=True)
    processor_speed = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    season = models.CharField(max_length=1, null=True)
    year = models.IntegerField(null=True, validators=[MinValueValidator(1976), MaxValueValidator(datetime.now().year)])
    storage = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    ram = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name="RAM")
    gpu = models.ForeignKey(DeviceGPU, on_delete=models.PROTECT, null=True, verbose_name="GPU")
    functional_attributes = models.ManyToManyField(DeviceFunctionalAttribute)
    serial_number = models.CharField(max_length=20, null=True)
    description = models.TextField(null=True)

    @property
    def sku(self) -> str:
        """Generate SKU from functionallity"""
        sku_parts = []
        skip_fields = ["id", "description"]
        # Iterate over the model fields
        for field in self._meta.fields:
            if field.name in skip_fields:
                continue
            field_value = getattr(self, field.name)
            if field_value is not None:
                # Check if the field is a Decimal
                if isinstance(field, models.DecimalField):
                    field_value = self.strip_for_sku(field_value)
                if isinstance(field_value, models.Model):
                    # Access the related object and retrieve the code attribute
                    field_code = getattr(field_value, "code", None)
                    if field_code is not None:
                        sku_parts.append(str(field_code))
                    else:
                        sku_parts.append(str(field_value))
                else:
                    sku_parts.append(str(field_value))

        return "-".join(sku_parts)

    def save(self, *args, **kwargs):
        """Save method do not update."""
        if self.pk:
            raise ValidationError("Cannot update existing listing.")
        listings = Device.objects.all().filter(device=self.device_type, part=self.part)
        for listing in listings:
            if listing.sku == self.sku:
                raise ValidationError("SKU already exists.")

        super().save(*args, **kwargs)

    @staticmethod
    def strip_for_sku(value: None | Decimal) -> str:
        """Strip value for SKU."""
        if value == 0:
            return "0"

        return str(value).replace(".", "").rstrip("0")


class DevicePartField(models.Model):
    """Visible fields for combination of device and part"""

    device = models.ForeignKey(DeviceType, on_delete=models.PROTECT)
    part = models.ForeignKey(DevicePart, on_delete=models.PROTECT)
    visible_fields = models.JSONField(default=dict)

    class Meta:
        unique_together = ["device", "part"]

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.device} - {self.part}"
