from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from . import views
from .views import PrintListView

urlpatterns = [
    path('', views.index, name='label_printer-home'),
    path('about', views.about, name='label_printer-about'),
    path('api/wo_label', views.workorder_label, name='label_printer-api-workorder_label'),
    path('api/rc_send_message', views.ring_central_send_message,
         name='label_printer-api-rc_send_message')
]
urlpatterns += staticfiles_urlpatterns()
