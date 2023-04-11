"""Forms to work on customer app"""
from django import forms
from crispy_forms.helper import FormHelper
from .models import Workorder


class WorkorderForm(forms.ModelForm):
    """Form to display and edit customer data"""

    class Meta:
        model = Workorder
        fields = [
            "ls_workorder_id",
            "time_in",
            "eta_out",
            "note",
            "warranty",
            "tax",
            "archived",
            "total",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
