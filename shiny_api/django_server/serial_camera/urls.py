"""URLs for the API app.""" ""
from django.urls import path

from . import views

app_name = "serial_camera"

urlpatterns = [
    path("", views.home, name="home"),
]
