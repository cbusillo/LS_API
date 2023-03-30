"""View for LS Functions"""
from importlib import import_module
from threading import Thread
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
# from django_eventstream import send_event
from shiny_api.django_server.settings import running_function
from pydantic import BaseModel

from shiny_api.modules.load_config import Config
from shiny_api.modules.label_print import print_text


class LabelGroup(BaseModel):
    """Class to hold label group data"""

    name: str
    labels: list[str]
    printer_ip: str

    @staticmethod
    def load_from_defaults():
        """Load label groups from config.DEFAULT_LABELS"""
        return {name: LabelGroup(name=name, labels=label_group["labels"], printer_ip=label_group["printer_ip"])
                for name, label_group in Config.DEFAULT_LABELS.items()}


def label_printer(request: WSGIRequest, active_label_group: str = "Main Labels"):
    """View to print labels"""
    label_group_list: dict[str, LabelGroup] = LabelGroup.load_from_defaults()
    label_group_name_list = list(label_group_list)
    quantity = int(request.POST.get("quantity", 1))
    label_text = ""
    context = {}

    if bool(request.POST.get("custom_label_print", False)):
        label_text = request.POST.get("custom_label_text", "")
    else:
        label_text = label_text or request.POST.get("label_text", "")
    lines = label_text.split("\n")
    while "" in lines:
        lines.remove("")
    label_text = lines
    if len(label_text) == 0 or quantity < 1:
        context["error"] = "No label text"
    else:
        print(f"Printing {label_text} to {label_group_list[active_label_group].printer_ip}...")
        try:
            print_text(quantity=quantity,
                       barcode=request.POST.get("barcode", ""),
                       print_date=bool(request.POST.get("date", False)),
                       text=label_text,
                       printer_ip=label_group_list[active_label_group].printer_ip)
        except TimeoutError as error:
            context["error"] = error

    context = {
        "title": "Label Printer",
        "label_group_name_list": label_group_name_list,
        "active_labels": label_group_list[active_label_group].labels,
        "active_label_group": active_label_group,
    }

    return render(request, 'labels.django-html', context)
