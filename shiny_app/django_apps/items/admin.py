from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import Item, Serial


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("ls_item_id", "description", "price", "archived", "serialized", "manufacturer_sku")
    list_filter = ("archived", "item_type", "serialized")
    search_fields = ("ls_item_id", "description", "custom_sku", "manufacturer_sku")


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
        "item__description",
    )
    readonly_fields = ("id",)
    autocomplete_fields = ("customer", "item")
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 2, "cols": 40})},
    }
