"""Websockets server"""
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from shiny_app.django_server.functions.routing import websocket_urlpatterns as ls_urls
from shiny_app.django_server.serial_camera.routing import websocket_urlpatterns as camera_urls
from shiny_app.django_server.sickw.routing import websocket_urlpatterns as sickw_urls


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shiny_app.django_server.settings")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(ls_urls + camera_urls + sickw_urls))),
    }
)
