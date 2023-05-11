"""Admin for items app.""" ""
from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.forms.widgets import CheckboxSelectMultiple
from .models import (
    Item,
    Serial,
    DeviceType,
    DevicePart,
    DevicePartField,
    DeviceFunctionalAttribute,
    DeviceProcessorType,
    DeviceGPU,
    Device,
)
from .forms import DeviceForm


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Admin for items."""

    list_display = ("ls_item_id", "description", "price", "archived", "serialized", "manufacturer_sku")
    list_filter = ("archived", "item_type", "serialized")
    search_fields = ("ls_item_id", "description", "custom_sku", "manufacturer_sku")


@admin.register(Serial)
class SerialAdmin(admin.ModelAdmin):
    """Admin for serials."""

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


class DeviceCodeNameAdmin(admin.ModelAdmin):
    """Abstract admin for code/name pairs."""

    list_display = ("code", "name", "sort_order")
    list_editable = ("name", "sort_order")
    change_list_template = "admin/items/code_change_list.html"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("code",)
        return ()

    class Meta:
        """Meta class."""

        abstract = True


@admin.register(DeviceFunctionalAttribute)
class DeviceFunctionalAttributeAdmin(DeviceCodeNameAdmin):
    """Admin for functional attributes."""

    pass  # pylint: disable=unnecessary-pass


@admin.register(DeviceType)
class DeviceTypeAdmin(DeviceCodeNameAdmin):
    """Admin for devices."""

    pass  # pylint: disable=unnecessary-pass


@admin.register(DeviceProcessorType)
class DeviceProcessorTypeAdmin(DeviceCodeNameAdmin):
    """Admin for processor types."""

    pass  # pylint: disable=unnecessary-pass


@admin.register(DeviceGPU)
class DeviceGPUAdmin(DeviceCodeNameAdmin):
    """Admin for GPUs."""

    pass  # pylint: disable=unnecessary-pass


@admin.register(DevicePart)
class DevicePartAdmin(DeviceCodeNameAdmin):
    """Admin for parts."""

    pass  # pylint: disable=unnecessary-pass


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """Admin for listings."""

    form = DeviceForm
    list_display = [field.name for field in Device._meta.get_fields() if field.concrete and field.many_to_many is False]  # type: ignore #pylint: disable=line-too-long
    list_display.append("sku")
    readonly_fields = ("sku",)
    formfield_overrides = {
        models.ManyToManyField: {"widget": CheckboxSelectMultiple},
    }

    class Media:
        js = (
            "https://code.jquery.com/jquery-3.6.4.min.js",
            "js/items/admin/get_visible_fields.js",
        )


@admin.register(DevicePartField)
class DevicePartFieldsAdmin(admin.ModelAdmin):
    """Connect devices and parts to needed fields"""

    list_display = ("device", "part", "visible_fields_as_list")
    list_filter = ("device", "part")

    def visible_fields_as_list(self, obj):
        """Return visible fields as a list.""" ""
        return ", ".join([f"{k}: {v}" for k, v in obj.visible_fields.items()])

    visible_fields_as_list.short_description = "Visible Fields"
