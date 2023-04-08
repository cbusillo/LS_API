"""URLs for the LS Functions app.""" ""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.label_printer, name="label_printer"),
    path("<active_label_group>/", views.label_printer, name="label_printer"),
]
