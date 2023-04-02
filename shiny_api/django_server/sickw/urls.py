"""URLs for the sickw app.""" ""
from django.urls import path  # type: ignore

from . import views  # pylint: disable=no-name-in-module

urlpatterns = [
    path("", views.bulk_lookup, name="sickw-bulk_lookup"),

]
