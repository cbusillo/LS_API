"""Urls for ls_function app"""
from django.urls import re_path  # type: ignore

from . import consumers

websocket_urlpatterns = [
    re_path("ls_functions/stream/", consumers.LsFunctionsConsumer.as_asgi()),
]
