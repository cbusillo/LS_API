"""Forms to work on customer app"""
from django import forms


class CustomerSearchForm(forms.Form):
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
