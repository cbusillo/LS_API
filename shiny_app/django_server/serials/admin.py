"""Serial admin."""
from django.contrib import admin
from django.db import models
from django.forms import Textarea
from ..serials.models import Serial
from ..customers.models import Customer
from ..items.models import Item


@admin.register(Serial)
class SerialAdmin(admin.ModelAdmin):
    list_display = ("id", "value_1", "value_2", "serial_number", "description", "customer", "item")
    search_fields = (
        "value_1",
        "value_2",
        "serial_number",
        "description",
        "customer__first_name",
        "customer__last_name",
        "item__name",
    )
    readonly_fields = ("id",)
    autocomplete_fields = ("customer", "item")
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 2, "cols": 40})},
    }
