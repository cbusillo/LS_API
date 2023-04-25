"""URLs for the Workorders app.""" ""
from django.urls import path
from . import views

app_name = "workorders"

urlpatterns = [
    path("create_workorder/", views.create_workorder_view, name="create_workorder"),
]
