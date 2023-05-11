"""URLs for the eBay app."""

from django.urls import path
from . import views

app_name = "ebay"

urlpatterns = [
    path("get_visible_fields/", views.get_visible_fields, name="get_visible_fields"),
]
