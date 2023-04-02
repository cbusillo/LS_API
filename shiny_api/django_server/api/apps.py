"""Configure Api App"""
from django.apps import AppConfig  # type: ignore


class ApiConfig(AppConfig):
    """Class to name Api APP"""
    name = 'shiny_api.django_server.api'
    label = 'api'
