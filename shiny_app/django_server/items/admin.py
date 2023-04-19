from django.contrib import admin
from .models import Item


class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "average_cost", "price")
    search_fields = ("name", "description")
    readonly_fields = ("id",)


admin.site.register(Item, ItemAdmin)
