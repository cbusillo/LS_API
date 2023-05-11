from django import forms
from .models import Listing


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in Listing._meta.get_fields():
            if field.name == "id":
                continue
            self.fields[field.name].required = False
