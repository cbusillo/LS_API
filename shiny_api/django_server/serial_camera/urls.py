"""URLs for the API app.""" ""
from django.urls import path  # type: ignore

from . import views

urlpatterns = [
    path("", views.index, name="serial_camera-index"),
]
