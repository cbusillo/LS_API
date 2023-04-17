"""URLs for the API app.""" ""
from django.urls import path
from . import views

app_name = "customers"

urlpatterns = [
    path("customer_list/", views.CustomerListView.as_view(), name="customer_list"),
]
