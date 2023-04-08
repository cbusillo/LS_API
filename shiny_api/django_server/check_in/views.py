"""App to check customers in"""
from django.http import JsonResponse
from django.shortcuts import render
from shiny_api.django_server.customers.models import Customer
from . import forms


def partial_form_data(request):
    """Receive form data as it is being entered"""

    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        data = request.POST.get("text_data")
        customers = Customer.objects.filter(last_name__icontains=data)
        test = " ".join([customer.first_name for customer in customers])
        response_data = {"message": f"Received data: {test}"}
        return JsonResponse(response_data)

    return JsonResponse({"message": "Invalid request."}, status=400)


def home(request):
    """Render home page"""
    customers = Customer.objects.all()
    check_in_form = forms.CheckIn(customers=customers)
    context = {"form": check_in_form}
    return render(request, "check_in/home.html", context)
