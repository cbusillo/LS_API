"""Admin for eBay app."""

from django.db import models
from django.forms import CheckboxSelectMultiple
from django.contrib import admin
from .models import DevicePartField, FunctionalAttribute, Device, Part, ProcessorType, GPU, Listing
from .forms import ListingForm


class CodeNameAdmin(admin.ModelAdmin):
    """Abstract admin for code/name pairs."""

    list_display = ("code", "name", "sort_order")
    list_editable = ("name", "sort_order")
    change_list_template = "admin/ebay/code_change_list.html"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("code",)
        return ()

    class Meta:
        """Meta class."""

        abstract = True


@admin.register(FunctionalAttribute)
class FunctionalAttributeAdmin(CodeNameAdmin):
    """Admin for functional attributes."""

    pass  # pylint: disable=unnecessary-pass


@admin.register(Device)
class DeviceAdmin(CodeNameAdmin):
    """Admin for devices."""

    pass  # pylint: disable=unnecessary-pass


@admin.register(ProcessorType)
class ProcessorTypeAdmin(CodeNameAdmin):
    """Admin for processor types."""

    pass  # pylint: disable=unnecessary-pass


@admin.register(GPU)
class GPUAdmin(CodeNameAdmin):
    """Admin for GPUs."""

    pass  # pylint: disable=unnecessary-pass


@admin.register(Part)
class PartAdmin(CodeNameAdmin):
    """Admin for parts."""

    pass  # pylint: disable=unnecessary-pass


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """Admin for listings."""

    form = ListingForm
    list_display = [field.name for field in Listing._meta.get_fields() if field.concrete and field.many_to_many is False]  # type: ignore
    list_display.append("sku")
    readonly_fields = ("sku",)
    formfield_overrides = {
        models.ManyToManyField: {"widget": CheckboxSelectMultiple},
    }

    class Media:
        js = (
            "https://code.jquery.com/jquery-3.6.4.min.js",
            "js/ebay/admin/get_visible_fields.js",
        )


@admin.register(DevicePartField)
class DevicePartFieldsAdmin(admin.ModelAdmin):
    list_display = ("device", "part", "visible_fields_as_list")
    list_filter = ("device", "part")

    def visible_fields_as_list(self, obj):
        return ", ".join([f"{k}: {v}" for k, v in obj.visible_fields.items()])

    visible_fields_as_list.short_description = "Visible Fields"
