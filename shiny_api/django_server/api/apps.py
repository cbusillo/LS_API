"""Configure Api App"""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Class to name Api APP"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shiny_api.django_server.api'
    label = 'api_view'
