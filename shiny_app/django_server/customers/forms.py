"""Forms to work on customer app"""
from django import forms
from django.db.models import Q
from django.urls import reverse_lazy
from crispy_forms.helper import FormHelper
from phonenumber_field.formfields import PhoneNumberField
from .models import Customer, Phone, Email


class CustomerSearch(forms.Form):
    """Form for check_in app."""

    last_name_input = forms.CharField(
        label="",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search Last Name", "autocomplete": "off", "autocorrect": "off"}),
    )
    first_name_input = forms.CharField(
        label="",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search First Name", "autocomplete": "off", "autocorrect": "off"}),
    )
    phone_number_input = forms.CharField(
        label="",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search Phone Number", "autocomplete": "off", "autocorrect": "off"}),
    )
    email_address_input = forms.CharField(
        label="",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search Email Address", "autocomplete": "off", "autocorrect": "off"}),
    )
    everything_input = forms.CharField(
        label="",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search Everything", "autocomplete": "off", "autocorrect": "off"}),
    )

    customer_output = forms.ModelChoiceField(
        label="Customers", required=False, queryset=None, widget=forms.Select(attrs={"size": 15}), empty_label=None
    )

    def __init__(self, *args, **kwargs):
        customers = kwargs.pop("customers", None)
        super().__init__(*args, **kwargs)

        if customers:
            self.fields["customer_output"].queryset = customers

        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.form_id = "customer_search_form"
        self.helper.attrs = {"autocomplete": "off", "data-url": reverse_lazy("check_in:partial_customer_form_data")}

    def get_customer_options(self, last_name: str, first_name: str, phone_number: str, email_address: str, everything: str):
        """Get customer options for select"""
        customer_filter = Q()
        if everything:
            customer_filter = (
                Q(last_name__icontains=everything)
                | Q(first_name__icontains=everything)
                | Q(phones__number__icontains=everything)
                | Q(emails__address__icontains=everything)
                | Q(company__icontains=everything)
                | Q(serials_related__serial_number__icontains=everything)
            )
        else:
            if last_name:
                customer_filter &= Q(last_name__icontains=last_name)
            if first_name:
                customer_filter &= Q(first_name__icontains=first_name)
            if phone_number:
                customer_filter &= Q(phones__number__icontains=phone_number)
            if email_address:
                customer_filter &= Q(emails__address__icontains=email_address)

        if filter_has_value(customer_filter):
            order_by = "last_name", "first_name"
        else:
            order_by = ("-update_time",)
        customers = Customer.objects.filter(customer_filter).distinct().order_by(*order_by)[:100]
        self.fields["customer_output"].queryset = customers
        return str(self["customer_output"].as_widget())

    def get_customer_list(self, first_name, last_name, phone_number, email_address):
        """Get customer list for display"""
        customer_filter = Q()
        if last_name:
            customer_filter &= Q(last_name__icontains=last_name)
        if first_name:
            customer_filter &= Q(first_name__icontains=first_name)
        if phone_number:
            customer_filter &= Q(phones__number__icontains=phone_number)
        if email_address:
            customer_filter &= Q(emails__address__icontains=email_address)
        order_by = "last_name", "first_name"
        customers = Customer.objects.filter(customer_filter).distinct().order_by(*order_by)
        return customers


def filter_has_value(query_filter: Q) -> bool:
    """Check for any values in filter"""
    for child in query_filter.children:
        if isinstance(child, Q):
            if filter_has_value(child):
                return True
        else:
            _, value = child
            if value:
                return True
    return False


class CustomerForm(forms.ModelForm):
    """Form to display and edit customer data"""

    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "title", "company", "archived", "update_from_ls_time"]
        readonly_fields = "update_from_ls_time"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.fields["first_name"].widget.attrs["class"] = "no-border text-end form-control-lg"
        self.fields["first_name"].field_id = "search_first_name_detail"
        self.fields["last_name"].widget.attrs["class"] = "no-border form-control-lg"
        self.fields["last_name"].field_id = "search_last_name_detail"


class PhoneForm(forms.ModelForm):
    """Form to display and edit phone data"""

    number = PhoneNumberField()

    class Meta:
        model = Phone
        fields = ["number", "number_type"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.fields["number_type"].widget.attrs["class"] = "no-border text-center form-control-sm"


class EmailForm(forms.ModelForm):
    """Form to display and edit email data"""

    class Meta:
        model = Email
        fields = ["address", "address_type"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.fields["address_type"].widget.attrs["class"] = "no-border text-center form-control-sm"
