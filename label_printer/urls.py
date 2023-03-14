from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='label_printer-home'),
    path('api/wo_label', views.workorder_label, name='label_printer-api-workorder_label'),
    path('api/rc_send_message', views.ring_central_send_message,
         name='label_printer-api-rc_send_message')
]
