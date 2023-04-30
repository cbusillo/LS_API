"""App to check customers in"""

from django.shortcuts import redirect, render
from shiny_app.modules.light_speed import import_all

from .models import Customer


def check_in(request):
    """Render home page"""
    customers = Customer.objects.all().order_by("-update_time")[:100]
    if customers.count() == 0:
        return redirect("functions:home")
    import_all()

    return render(request, "customers/check_in.html")
