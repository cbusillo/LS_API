from django.contrib import admin
from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("ls_item_id", "description", "price", "archived", "serialized", "manufacturer_sku")
    list_filter = ("archived", "item_type", "serialized")
    search_fields = ("ls_item_id", "description", "custom_sku", "manufacturer_sku")
