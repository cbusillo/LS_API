"""URLs for the Items app.""" ""

from django.urls import path
from .views import DeviceTestsView, DeviceSpecificationsView, TestInstanceView


app_name = "checklists"

urlpatterns = [
    path("device/<int:device_type_id>/<int:device_part_id>/tests/", DeviceTestsView.as_view(), name="device_tests"),
    path(
        "device/<int:device_type_id>/<int:device_part_id>/specifications/",
        DeviceSpecificationsView.as_view(),
        name="device_specifications",
    ),
    path("test_instance/", TestInstanceView.as_view(), name="test_instance"),
]
