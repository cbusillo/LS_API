"""Urls for function app"""
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/functions/", consumers.LsFunctionsConsumer.as_asgi()),
]
