"""URLs for the API app.""" ""
from django.urls import path
from .tables import CustomerTable

app_name = "customers"

urlpatterns = [
    path("customer_data/", CustomerTable.as_view(), name="customer_data"),
]
