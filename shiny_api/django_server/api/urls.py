"""URLs for the API app."""""
from django.urls import path  # type: ignore

from . import views

urlpatterns = [
    path('wo_label/', views.workorder_label, name='workorder_label'),
    path('rc_send_message/', views.ring_central_send_message, name='ring_central_send_message'),
]
