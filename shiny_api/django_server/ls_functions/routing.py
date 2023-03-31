"""Urls for ls_function app"""
from django.urls import path  # type: ignore

from . import consumers

websocket_urlpatterns = [
    path("stream/", consumers.LsFunctionsConsumer.as_asgi()),
]
