"""Form for check_in app."""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field


class CheckIn(forms.Form):
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
    text_output = forms.CharField(label="Output Label", required=False)
    customer_output = forms.ModelChoiceField(
        label="Customers", required=False, queryset=None, widget=forms.Select(attrs={"size": 10})
    )

    def __init__(self, *args, **kwargs):
        customers = kwargs.pop("customers", None)
        super().__init__(*args, **kwargs)

        if customers:
            self.fields["customer_output"].queryset = customers

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("first_name_input", css_class="form-control"),
            Field("last_name_input", css_class="form-control"),
            Field("customer_output", css_class="form-select"),
            Field("text_output", css_class="form-control", placeholder=""),
        )
