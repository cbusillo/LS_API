"""Form for adding and editing items.""" ""
from django import forms
from .models import Device


class DeviceForm(forms.ModelForm):
    """Make fields not required in form."""

    class Meta:
        model = Device
        exclude = []  #  pylint: disable=modelform-uses-exclude

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in Device._meta.get_fields():
            if field.name == "id":
                continue
            self.fields[field.name].required = False
