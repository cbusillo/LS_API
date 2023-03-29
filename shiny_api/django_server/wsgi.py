"""
WSGI config for django_poetry_example project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault(key='DJANGO_SETTINGS_MODULE', value='shiny_api.django_server.settings')

application = get_wsgi_application()
