"""Urls for sickw app"""
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/sickw/", consumers.SickwConsumer.as_asgi()),
]
