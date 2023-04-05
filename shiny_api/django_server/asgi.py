"""Websockets server"""
import os

from channels.auth import AuthMiddlewareStack  # type: ignore
from channels.routing import ProtocolTypeRouter, URLRouter  # type: ignore
from channels.security.websocket import AllowedHostsOriginValidator  # type: ignore
from django.core.asgi import get_asgi_application  # type: ignore

from shiny_api.django_server.ls_functions.routing import websocket_urlpatterns as ls_urls
from shiny_api.django_server.serial_camera.routing import websocket_urlpatterns as camera_urls


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shiny_api.django_server.settings")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(ls_urls + camera_urls))),
    }
)
