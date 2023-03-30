# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path("ls_functions/stream/", consumers.LsFunctionsConsumer.as_asgi()),
]
