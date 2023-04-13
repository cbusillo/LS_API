"""Urls for check_in app.""" ""
from django.urls import path
from . import views

app_name = "check_in"

urlpatterns = [
    path("", views.home, name="home"),
    path("partial_customer_form_data/", views.partial_customer_form_data, name="partial_customer_form_data"),
    path("create_workorder/", views.create_workorder_view, name="create_workorder"),
]
