"""URLs for the LS Functions app."""""
from django.urls import path  # type: ignore

from . import views

urlpatterns = [
    path('', views.ls_functions, name='ls_functions'),
    path('<module_function_name>/', views.ls_functions, name='ls_functions'),
    # path('stream/', views.stream, name='stream')
]
