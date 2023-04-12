"""View for API access to Shiny Stuff"""

from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View

from .forms import ItemSearchForm
from .models import Item


class ItemListView(View):
    """View for listing items"""

    def get(self, request):
        """Create form on GET request and list items"""
        form = ItemSearchForm(request.GET)
        items = Item.objects.all()

        if form.is_valid():
            description = form.cleaned_data.get("description")
            if description:
                items = items.filter(description__icontains=description)

        paginator = Paginator(items, 25)  # Show 25 items per page.
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, "inventory/item_list.html", {"form": form, "page_obj": page_obj})
