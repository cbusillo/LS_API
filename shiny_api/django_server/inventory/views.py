"""View for API access to Shiny Stuff"""

from django.views.generic import ListView
from .models import Item


class ItemListView(ListView):
    """List view for Shiny Items"""

    model = Item
    template_name = "inventory/items_list_view.html"
    context_object_name = "items"
