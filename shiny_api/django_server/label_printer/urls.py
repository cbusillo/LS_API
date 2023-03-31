"""URLs for the LS Functions app.""" ""
from django.urls import path  # type: ignore

from . import views  # pylint: disable=no-name-in-module

urlpatterns = [
    path("", views.label_printer, name="label_printer"),
    path("<active_label_group>/", views.label_printer, name="label_printer"),
]
