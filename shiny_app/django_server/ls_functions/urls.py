"""URLs for the LS Functions app.""" ""
from django.urls import path

from . import views

app_name = "ls_functions"

urlpatterns = [
    path("", views.ls_functions, name="home"),
    path("<module_function_name>/", views.ls_functions, name="home"),
]
