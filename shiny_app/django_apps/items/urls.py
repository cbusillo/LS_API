"""URLs for the Items app.""" ""

from django.urls import path
from . import views


app_name = "items"

urlpatterns = [
    path("get_device_visible_fields/", views.get_device_visible_fields, name="get_device_visible_fields"),
]
