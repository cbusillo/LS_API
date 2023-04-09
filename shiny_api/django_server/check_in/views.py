"""App to check customers in"""
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from shiny_api.django_server.customers.models import Customer
from ..customers.forms import CustomerDetailForm, CustomerSearch


def partial_customer_form_data(request):
    """Receive form data as it is being entered"""
    form = CustomerSearch(request.POST or None)
    if form.is_valid():
        last_name = form.cleaned_data.get("last_name_input")
        first_name = form.cleaned_data.get("first_name_input")
        html_customer_output = form.get_customer_options(last_name, first_name)

        test_output = html_customer_output

        customer_id = request.POST.get("customer_id")
        if customer_id:
            customer = Customer.objects.get(id=customer_id)
            customer_detail_form = CustomerDetailForm(instance=customer)
            customer_detail_form_html = render_to_string(
                "customers/customer_detail.html",
                {"customer_detail_form": customer_detail_form},
                request=request,
            )
        else:
            customer_detail_form_html = None

        response_data = {
            "message": f"Received data: {test_output}",
            "html_customer_options": html_customer_output,
            "customer_detail_form": customer_detail_form_html,
        }
        return JsonResponse(response_data)

    return JsonResponse({"message": "Invalid request."}, status=400)


def home(request):
    """Render home page"""
    customers = Customer.objects.all().order_by("-update_time")[:15]
    if customers.count() == 0:
        return redirect("ls_functions:home")
    customer_search = CustomerSearch(customers=customers)

    context = {"customer_search_form": customer_search}
    return render(request, "check_in/home.html", context)
