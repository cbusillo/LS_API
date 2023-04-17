"""Forms to work on Items app"""
from django import forms


class ItemSearchForm(forms.Form):
    """Form for searching items"""

    description = forms.CharField(
        label="Description",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search by description..."}),
    )
