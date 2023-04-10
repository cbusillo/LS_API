"""Forms to work on customer app"""
from django import forms
from django.db.models import Q
from django.urls import reverse_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div
from phonenumber_field.formfields import PhoneNumberField
from .models import Customer, Phone


class CustomerSearchList(forms.Form):
    """Form for searching customers"""

    first_name = forms.CharField(
        label="First Name",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search by Name..."}),
    )

    last_name = forms.CharField(
        label="Last Name",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search by Name..."}),
    )


class CustomerSearch(forms.Form):
    """Form for check_in app."""

    last_name_input = forms.CharField(
        label="",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search Last Name",
                "autocomplete": "off",
                "autocorrect": "off",
            }
        ),
    )
    first_name_input = forms.CharField(
        label="",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search First Name", "autocomplete": "off", "autocorrect": "off"}),
    )
    text_output = forms.CharField(label="Output Label", required=False)
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

        self.helper.layout = Layout(
            Field("first_name_input", css_class="form-control"),
            Field("last_name_input", css_class="form-control"),
            Field("customer_output", css_class="form-select"),
            Field("text_output", css_class="form-control", placeholder=""),
        )

    def get_customer_options(self, last_name, first_name):
        """Get customer options for select"""
        customer_filter = Q(last_name__icontains=last_name) & Q(first_name__icontains=first_name)
        if filter_has_value(customer_filter):
            order_by = "last_name", "first_name"
        else:
            order_by = ("-update_time",)
        customers = Customer.objects.filter(customer_filter).order_by(*order_by)[:100]
        self.fields["customer_output"].queryset = customers
        return str(self["customer_output"].as_widget())


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
        fields = ["first_name", "last_name", "title", "company", "archived"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Div(
                Div(
                    Field("first_name"),
                    css_class="col",
                ),
                Div(
                    Field("last_name"),
                    css_class="col",
                ),
                css_class="row",
            ),
            Div(
                Field("title"),
                Field("company"),
                Field("archived"),
                css_class="row",
            ),
        )
        self.fields["first_name"].label = ""
        self.fields["last_name"].label = ""


class PhoneForm(forms.ModelForm):
    """Form to display and edit phone data"""

    number = PhoneNumberField()

    class Meta:
        model = Phone
        fields = ["number", "use_type"]

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", None)
        super().__init__(*args, **kwargs)
        self.prefix = prefix
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Field("number"),
                Field("use_type"),
                css_class="row",
            ),
        )
