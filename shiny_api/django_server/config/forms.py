from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy
from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper
from .models import Config


class ConfigListView(ListView):
    model = Config
    template_name = "config/config_list.html"
    context_object_name = "configs"


class ConfigEditView(UpdateView):
    model = Config
    template_name = "config/config_edit.html"
    fields = ["key", "value"]
    success_url = reverse_lazy("config-config_list")

    def get_context_data(self, **kwargs):
        data = super(ConfigEditView, self).get_context_data(**kwargs)
        if self.request.POST:
            data["helper"] = FormHelper()
            data["helper"].add_input(Submit("submit", "Save"))
        else:
            data["helper"] = FormHelper()
            data["helper"].add_input(Submit("submit", "Save"))
        return data
