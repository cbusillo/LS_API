"""Workorder Admin"""
from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import Workorder, WorkorderItem, WorkorderLine


class WorkorderItemInline(admin.StackedInline):
    model = WorkorderItem
    extra = 0
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 1, "cols": 20, "style": "height: 1em;"})},
    }


class WorkorderLineInline(admin.TabularInline):
    model = WorkorderLine
    extra = 1
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 1, "cols": 20, "style": "height: 1em;"})},
    }


class WorkorderAdmin(admin.ModelAdmin):
    inlines = [WorkorderItemInline, WorkorderLineInline]
    list_display = ("id", "customer", "status", "time_in", "total")
    search_fields = ("customer__first_name", "customer__last_name", "status", "time_in", "total")
    readonly_fields = ("id", "customer", "customer_info", "ls_workorder_id")

    def customer_info(self, obj):
        return f"First Name: {obj.customer.first_name}\nLast Name: {obj.customer.last_name}\nEmail: {obj.customer.emails.first().address if obj.customer.emails.first() else 'N/A'}\nPhone: {obj.customer.phones.first().number if obj.customer.phones.first() else 'N/A'}"

    customer_info.short_description = "Customer Information"


admin.site.register(Workorder, WorkorderAdmin)
