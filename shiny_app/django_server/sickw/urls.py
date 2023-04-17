"""URLs for the sickw app.""" ""
from django.urls import path

from . import views

app_name = "sickw"

urlpatterns = [
    path("", views.home, name="bulk_lookup"),
]
