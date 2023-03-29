import os
from django.core.asgi import get_asgi_application
from django.urls import path, re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import django_eventstream

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shiny_api.django_server.settings")

application = ProtocolTypeRouter({
    'http': URLRouter([
        path('stream/', AuthMiddlewareStack(
            URLRouter(django_eventstream.routing.urlpatterns)
        ), {'channels': ['status']}),
        re_path(r'', get_asgi_application()),
    ]),
})
