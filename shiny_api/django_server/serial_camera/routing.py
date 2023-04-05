"""Urls for ls_function app"""
from django.urls import path  # type: ignore

from . import consumers  # pylint: disable=no-name-in-module

websocket_urlpatterns = [
    path("ws/serial_camera/", consumers.CameraConsumer.as_asgi()),
]
