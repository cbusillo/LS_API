"""App to check customers in"""
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from shiny_api.modules.light_speed import import_customers
from ..customers.models import Customer
from ..customers.forms import CustomerSearch, CustomerForm, PhoneForm, EmailForm


def partial_customer_form_data(request):
    """Receive form data as it is being entered"""
    form = CustomerSearch(request.POST or None)
    if form.is_valid():
        last_name = form.cleaned_data.get("last_name_input")
        first_name = form.cleaned_data.get("first_name_input")
        phone_number = form.cleaned_data.get("phone_number_input")
        email_address = form.cleaned_data.get("email_address_input")
        customer_output_html = form.get_customer_options(last_name, first_name, phone_number, email_address)

        customer_id = request.POST.get("customer_id")
        if customer_id:
            customer = Customer.objects.get(id=customer_id)
            phones = customer.phones.all()
            emails = customer.emails.all()
            customer_detail_form = CustomerForm(instance=customer)
            customer_phone_forms = [PhoneForm(instance=phone) for phone in phones]
            customer_email_forms = [EmailForm(instance=email) for email in emails]

            customer_detail_form_html = render_to_string(
                "customers/customer_detail_form.html",
                {"customer_detail_form": customer_detail_form},
                request=request,
            )
            customer_phone_forms_html = ""
            for customer_phone_form in customer_phone_forms:
                customer_phone_forms_html += render_to_string(
                    "customers/customer_phone_form.html",
                    {"customer_phone_form": customer_phone_form},
                    request=request,
                )
            customer_email_forms_html = ""
            for customer_email_form in customer_email_forms:
                customer_email_forms_html += render_to_string(
                    "customers/customer_email_form.html",
                    {"customer_email_form": customer_email_form},
                    request=request,
                )

        else:
            customer_detail_form_html = None
            customer_phone_forms_html = None
            customer_email_forms_html = None

        response_data = {
            "customer_id": customer_id,
            "customer_options": customer_output_html,
            "customer_detail_form": customer_detail_form_html,
            "customer_phone_form": customer_phone_forms_html,
            "customer_email_form": customer_email_forms_html,
        }
        return JsonResponse(response_data)

    return JsonResponse({"message": "Invalid request."}, status=400)


def home(request):
    """Render home page"""
    import_customers()
    customers = Customer.objects.all().order_by("-update_time")[:15]
    customer_search = CustomerSearch(customers=customers)

    context = {"customer_search_form": customer_search}
    return render(request, "check_in/home.html", context)
