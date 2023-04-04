"""URLs for the API app.""" ""
from django.urls import path
from . import views

urlpatterns = [
    path("item/", views.ItemListView.as_view(), name="inventory-item_list"),
]
