"""Views for the ebay app.""" ""
from django.http import JsonResponse
from django.core.handlers.wsgi import WSGIRequest
from .models import DeviceType, DevicePart, Device


def get_device_visible_fields(request: WSGIRequest) -> JsonResponse:
    """Return visible fields for a given device and part."""
    # device_id = request.GET.get("device")
    # part_id = request.GET.get("part")

    visible_fields = {field.name: False for field in Device._meta.get_fields() if field.concrete}  # type: ignore

    if True:  # pylint: disable=using-constant-test
        for field in visible_fields:
            visible_fields[field] = True
    # visible_fields["device"] = True

    # if device_id:
    #     visible_fields["part"] = True

    # if device_id and part_id:
    #     device = DeviceType.objects.get(pk=device_id)
    #     part = DevicePart.objects.get(pk=part_id)

    #     if device.name.lower() == "iphone" and "complete" in part.name.lower():
    #         visible_fields["storage"] = True

    return JsonResponse({"visible_fields": visible_fields})
