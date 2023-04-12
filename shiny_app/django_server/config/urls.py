from django.urls import path
from . import views

app_name = "config"

urlpatterns = [
    path("", views.ConfigListView.as_view(), name="config_list"),
    path("edit/<int:pk>", views.ConfigEditView.as_view(), name="config_edit"),
]
