"""App to check customers in"""
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from shiny_api.django_server.customers.models import Customer
from . import forms


def partial_form_data(request):
    """Receive form data as it is being entered"""

    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        last_name = request.POST.get("last_name")
        first_name = request.POST.get("first_name")
        customers = Customer.objects.filter(Q(last_name__icontains=last_name) & Q(first_name__icontains=first_name))

        customers_list = [{"first_name": customer.first_name, "last_name": customer.last_name} for customer in customers]
        test_output = " ".join([customer.first_name for customer in customers])
        response_data = {"message": f"Received data: {test_output}", "customers": customers_list[:100]}
        return JsonResponse(response_data)

    return JsonResponse({"message": "Invalid request."}, status=400)


def home(request):
    """Render home page"""
    customers = Customer.objects.all()[:100]
    check_in_form = forms.CheckIn(customers=customers)
    context = {"form": check_in_form}
    return render(request, "check_in/home.html", context)
