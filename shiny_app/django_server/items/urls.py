"""URLs for the API app.""" ""
from django.urls import path
from . import views

app_name = "items"

urlpatterns = [
    path("item_list/", views.ItemListView.as_view(), name="item_list"),
]
