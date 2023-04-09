"""URLs for the API app.""" ""
from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path("item/", views.ItemListView.as_view(), name="item_list"),
]
