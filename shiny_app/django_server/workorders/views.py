"""Views for workorders app"""
from urllib.parse import parse_qs
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from .models import Workorder
from ..customers.models import Customer
from shiny_app.classes.ls_customer import Customer as LSCustomer
from shiny_app.modules.light_speed import import_customers, create_workorder


class WorkorderListView(LoginRequiredMixin, View):
    """View for listing items"""

    def get(self, request):
        """Create form on GET request and list items"""

        workorder = Workorder.objects.all()

        paginator = Paginator(workorder, 25)  # Show 25 items per page.
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, "workorders/workorder_list.html", {"page_obj": page_obj})


def create_workorder_view(request):
    """Create a work order for a customer"""
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request."}, status=400)
    customer_id = request.POST.get("customer_id")
    if customer_id:
        ls_customer_id = Customer.objects.get(id=customer_id).ls_customer_id
    else:
        serialized_customer = parse_qs(request.POST.get("form"))
        first_name = serialized_customer.get("first_name_input", [])[0]
        last_name = serialized_customer.get("last_name_input", [])[0]
        phone_number = serialized_customer.get("phone_number_input", [])[0]
        email_address = serialized_customer.get("email_address_input", [])[0]
        ls_customer = LSCustomer(
            first_name=first_name,
            last_name=last_name,
            phones=[{"number_type": "Mobile", "number": phone_number}],
            emails=[{"email_type": "Primary", "address": email_address}],
        )
        ls_customer_id = ls_customer.create()
    import_customers()
    if ls_customer_id:
        workorder_id = create_workorder(ls_customer_id)
        return JsonResponse({"workorder_id": workorder_id})

    return JsonResponse({})
