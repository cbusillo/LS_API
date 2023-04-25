"""URLs for the API app.""" ""
from django.urls import path
from . import views
from .tables import CustomerTable

app_name = "customers"

urlpatterns = [
    path("customer_list/", views.CustomerListView.as_view(), name="customer_list"),
    path("customer_data/", CustomerTable.as_view(), name="customer_data"),
]
