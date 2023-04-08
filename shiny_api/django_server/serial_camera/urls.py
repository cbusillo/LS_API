"""URLs for the API app.""" ""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="serial_camera-home"),
]
