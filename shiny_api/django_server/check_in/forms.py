"""Form for check_in app.""" ""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field


class CheckIn(forms.Form):
    """Form for check_in app."""

    text_input = forms.CharField(label="Input Label", required=False)
    text_output = forms.CharField(label="Output Label", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("text_input", css_class="form-control", placeholder="Type here"),
            Field("text_output", css_class="form-control", placeholder=""),
        )
