"""Configure Label Printer App"""
from django.apps import AppConfig  # type: ignore


class LabelPrinterConfig(AppConfig):
    """Class to name Label Printer App"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shiny_api.django_server.label_printer'
    label = 'label_printer'
