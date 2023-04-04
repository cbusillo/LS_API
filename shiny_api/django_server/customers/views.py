"""View for API access to Shiny Stuff"""

from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View

from .forms import CustomerSearchForm
from .models import Customer


class CustomerListView(View):
    """View for listing items"""

    def get(self, request):
        """Create form on GET request and list items"""
        form = CustomerSearchForm(request.GET)
        customers = Customer.objects.all()

        if form.is_valid():
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            if first_name:
                customers = customers.filter(first_name__icontains=first_name)
            if last_name:
                customers = customers.filter(last_name__icontains=last_name)

        paginator = Paginator(customers, 25)  # Show 25 items per page.
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, "customers/customer_list.html", {"form": form, "page_obj": page_obj})
