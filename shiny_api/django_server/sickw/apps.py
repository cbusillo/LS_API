"""Configure Sickw App"""
from django.apps import AppConfig  # type: ignore


class SickwPrinterConfig(AppConfig):
    """Class to name Label Printer App"""
    name = 'shiny_api.django_server.sickw'
    label = 'sickw'
