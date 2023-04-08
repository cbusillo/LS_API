"""Urls for check_in app.""" ""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="check_in-home"),
    path("partial_form_data/", views.partial_form_data, name="check_in-partial_form_data"),
]
