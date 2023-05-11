"""Views for the ebay app.""" ""
from django.http import JsonResponse
from django.core.handlers.wsgi import WSGIRequest
from .models import Device, Part, Listing


def get_visible_fields(request: WSGIRequest) -> JsonResponse:
    """Return visible fields for a given device and part."""
    device_id = request.GET.get("device")
    part_id = request.GET.get("part")

    visible_fields = {field.name: False for field in Listing._meta.get_fields() if field.concrete}  # type: ignore

    visible_fields["device"] = True

    if device_id:
        visible_fields["part"] = True

    if device_id and part_id:
        device = Device.objects.get(pk=device_id)
        part = Part.objects.get(pk=part_id)

        if device.name.lower() == "iphone" and "complete" in part.name.lower():
            visible_fields["storage"] = True

    return JsonResponse({"visible_fields": visible_fields})
