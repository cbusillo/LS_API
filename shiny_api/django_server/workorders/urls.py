"""URLs for the Workorders app.""" ""
from django.urls import path
from . import views

app_name = "workorders"

urlpatterns = [
    path("", views.WorkorderListView.as_view(), name="workorder_list"),
]
