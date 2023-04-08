"""URLs for the sickw app.""" ""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.bulk_lookup, name="sickw-bulk_lookup"),
]
