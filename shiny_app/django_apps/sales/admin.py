"""Sale Admin"""
from django.contrib import admin
from django.db import models
from django.forms import Textarea

from .models import Sale, SaleLine


class SaleLineInline(admin.StackedInline):
    """Sale Line"""

    model = SaleLine
    extra = 0
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 1, "cols": 20, "style": "height: 1em;"})},
    }


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """Sale Admin"""

    inlines = [SaleLineInline]
