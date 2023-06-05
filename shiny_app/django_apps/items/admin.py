from django.contrib import admin
from django.db.models import TextField
from django.forms import Textarea
from .models import (
    Item,
    Serial,
)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Admin for items."""

    list_display = (
        "ls_item_id",
        "description",
        "default_cost",
        "average_cost",
        "price",
        "tax",
        "archived",
        "item_type",
        "serialized",
        "model_year",
        "upc",
        "custom_sku",
        "manufacturer_sku",
        "create_time",
        "update_time",
        "update_from_ls_time",
        "item_matrix_id",
    )
    list_filter = ("archived", "item_type", "serialized")
    search_fields = ("ls_item_id", "description", "custom_sku", "manufacturer_sku")


@admin.register(Serial)
class SerialAdmin(admin.ModelAdmin):
    """Admin for serials."""

    list_display = (
        "ls_serial_id",
        "value_1",
        "value_2",
        "serial_number",
        "description",
        "create_time",
        "update_time",
        "update_from_ls_time",
        "item",
        "customer",
    )
    search_fields = (
        "value_1",
        "value_2",
        "serial_number",
        "description",
        "customer__first_name",
        "customer__last_name",
        "item__description",
    )
    readonly_fields = ("id",)
    autocomplete_fields = ("customer", "item")
    formfield_overrides = {
        TextField: {"widget": Textarea(attrs={"rows": 2, "cols": 40})},
    }
