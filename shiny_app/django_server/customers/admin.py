from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import Customer, Email, Phone
from ..workorders.models import Workorder
from ..serials.models import Serial
from ..serials.admin import SerialAdmin
from ..workorders.admin import WorkorderAdmin


class EmailInline(admin.TabularInline):
    model = Email
    extra = 1


class PhoneInline(admin.TabularInline):
    model = Phone
    extra = 1


class WorkorderInline(admin.TabularInline):
    model = Workorder
    extra = 0
    fields = ("id", "status", "note", "time_in", "total")
    readonly_fields = fields


class SerialInline(admin.TabularInline):
    model = Serial
    extra = 0
    fields = ("id", "value_1", "value_2", "serial_number", "description", "customer", "item")
    readonly_fields = fields
    autocomplete_fields = ("customer", "item")
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 2, "cols": 40})},
    }


class CustomerAdmin(admin.ModelAdmin):
    inlines = [EmailInline, PhoneInline, WorkorderInline, SerialInline]
    list_display = (
        "id",
        "first_name",
        "last_name",
        "company",
        "create_time",
        "update_time",
        "archived",
    )
    search_fields = (
        "first_name",
        "last_name",
        "company",
    )
    readonly_fields = (
        "id",
        "ls_customer_id",
        "contact_id",
        "credit_account_id",
        "customer_type_id",
        "tax_category_id",
        "update_from_ls_time",
    )

    def mobile_number(self, obj):
        return obj.mobile_number

    mobile_number.short_description = "Mobile Number"


admin.site.register(Customer, CustomerAdmin)
# admin.site.register(Workorder, WorkorderAdmin)
# admin.site.register(Serial, SerialAdmin)
