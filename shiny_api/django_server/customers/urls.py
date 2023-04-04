"""URLs for the API app.""" ""
from django.urls import path
from . import views

urlpatterns = [
    path("customer/", views.CustomerListView.as_view(), name="customer-customer_list"),
]
