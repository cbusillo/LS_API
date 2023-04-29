"""Views for workorders app"""
from time import sleep
from django.http import JsonResponse
from shiny_app.classes.ls_customer import Customer as LSCustomer
from shiny_app.modules.light_speed import create_workorder, import_customers

from ..customers.models import Customer


def create_workorder_view(request):
    """Create a work order for a customer"""
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request."}, status=400)
    customer_id = request.POST.get("customer_id")
    if customer_id:
        ls_customer_id = Customer.objects.get(id=customer_id).ls_customer_id
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")
        email_address = request.POST.get("email_address")
        ls_customer = LSCustomer(
            first_name=first_name,
            last_name=last_name,
            phones=[{"number_type": "Mobile", "number": phone_number}],
            emails=[{"email_type": "Primary", "address": email_address}],
        )
        ls_customer_id = ls_customer.create()
        sleep(0.5)
        import_customers()

    if ls_customer_id:
        workorder_id = create_workorder(ls_customer_id)
        return JsonResponse({"workorder_id": workorder_id})

    return JsonResponse({})
