import datetime
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

from .models import TestInstance, TestInstanceResult, TestInstanceSpecification, Device


class TestInstanceForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("device_type", css_class="form-control"),
            Field("device_part", css_class="form-control"),
            Field("technician", css_class="form-control"),
            Field("date", css_class="form-control"),
        )
        self.fields["date"].initial = datetime.date.today()

    class Meta:
        model = TestInstance
        fields = ["device_type", "device_part", "technician", "date"]


class TestInstanceResultForm(forms.ModelForm):
    class Meta:
        model = TestInstanceResult
        fields = ["test_instance", "test", "result", "comment"]


class TestInstanceSpecificationForm(forms.ModelForm):
    class Meta:
        model = TestInstanceSpecification
        fields = ["test_instance", "specification", "value"]
