"""URLs for the Serial app.""" ""
from django.urls import path
from . import views

app_name = "serials"

urlpatterns = [
    path("serial_list", views.SerialListView.as_view(), name="serial_list"),
]
