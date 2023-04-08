"""URLs for the LS Functions app.""" ""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.ls_functions, name="ls_functions"),
    path("<module_function_name>/", views.ls_functions, name="ls_functions"),
]
