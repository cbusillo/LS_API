"""Configure Customer App"""
from django.apps import AppConfig


class CustomerConfig(AppConfig):
    """Class to name Inventory app"""

    name = "shiny_api.django_server.customers"
    label = "customers"
