"""URLs for the API app.""" ""
from django.urls import path
from . import tables
from . import views

app_name = "customers"

urlpatterns = [
    path("customer_data/", tables.CustomerTable.as_view(), name="customer_data"),
    path("check_in/", views.check_in, name="check_in"),
]
