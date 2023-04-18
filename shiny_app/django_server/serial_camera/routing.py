"""Urls for function app"""
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/serial_camera/", consumers.CameraConsumer.as_asgi()),
]
