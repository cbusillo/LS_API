"""Urls for check_in app.""" ""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="check_in-home"),
    path("get_text_data/", views.get_text_data, name="check_in-get_text_data"),
]
