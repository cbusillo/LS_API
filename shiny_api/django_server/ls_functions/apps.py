"""Configure LS Functions App"""
from django.apps import AppConfig  # type: ignore


class LsFunctionsConfig(AppConfig):
    """Class to name Api APP"""
    name = 'shiny_api.django_server.ls_functions'
    label = 'ls_functions'
