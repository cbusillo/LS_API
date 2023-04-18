"""View for API access to Shiny Stuff"""

from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View

from .forms import CustomerSearch
from .models import Customer


class CustomerListView(View):
    """View for listing items"""

    def get(self, request):
        """Create form on GET request and list items"""
        form = CustomerSearch(request.GET)

        if form.is_valid():
            first_name = form.cleaned_data.get("first_name_input", None)
            last_name = form.cleaned_data.get("last_name_input", None)
            phone_number = form.cleaned_data.get("phone_number_input", None)
            email_address = form.cleaned_data.get("email_address_input", None)
            customers = form.get_customer_list(first_name, last_name, phone_number, email_address)
        else:
            customers = Customer.objects.all()

        paginator = Paginator(customers, 25)  # Show 25 items per page.
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, "customers/customer_list.html", {"form": form, "page_obj": page_obj})
