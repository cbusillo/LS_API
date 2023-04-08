from django.urls import path
from . import views

urlpatterns = [
    path("", views.ConfigListView.as_view(), name="config-config_list"),
    path("edit/<int:pk>", views.ConfigEditView.as_view(), name="config-config_edit"),
]
