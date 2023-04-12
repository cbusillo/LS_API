"""URLs for the LS Functions app.""" ""
from django.urls import path

from . import views

app_name = "label_printer"

urlpatterns = [
    path("", views.label_printer, name="home"),
    path("<active_label_group>/", views.label_printer, name="home"),
]
