"""Shiny eBay listing model."""
from datetime import datetime
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class CodeNameModel(models.Model):
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


class FunctionalAttribute(CodeNameModel):
    """Listing functional attribute choices."""

    pass  # pylint: disable=unnecessary-pass


class Device(CodeNameModel):
    """Listing type choices."""

    pass  # pylint: disable=unnecessary-pass


class Part(CodeNameModel):
    """Listing part choices."""

    pass  # pylint: disable=unnecessary-pass


class ProcessorType(CodeNameModel):
    """Listing processor choices."""

    pass  # pylint: disable=unnecessary-pass


class GPU(CodeNameModel):
    """Listing GPU choices."""

    class Meta:
        verbose_name = "GPU"
        verbose_name_plural = "GPUs"


class Listing(models.Model):
    """eBay listing model."""

    device = models.ForeignKey(Device, on_delete=models.PROTECT)
    part = models.ForeignKey(Part, on_delete=models.PROTECT)
    processor_type = models.ForeignKey(ProcessorType, on_delete=models.PROTECT, null=True)
    processor_speed = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    season = models.CharField(max_length=1, null=True)
    year = models.IntegerField(null=True, validators=[MinValueValidator(1976), MaxValueValidator(datetime.now().year)])
    storage = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    ram = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name="RAM")
    gpu = models.ForeignKey(GPU, on_delete=models.PROTECT, null=True, verbose_name="GPU")
    functional_attributes = models.ManyToManyField(FunctionalAttribute)
    description = models.TextField(null=True)

    @property
    def sku(self) -> str:
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
        listings = Listing.objects.all().filter(device=self.device, part=self.part)
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
    device = models.ForeignKey(Device, on_delete=models.PROTECT)
    part = models.ForeignKey(Part, on_delete=models.PROTECT)
    visible_fields = models.JSONField(default=dict)

    class Meta:
        unique_together = ["device", "part"]

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.device} - {self.part}"
