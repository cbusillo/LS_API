"""View for API access to Shiny Stuff"""
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from shiny_app.modules.light_speed import import_workorders

from ..workorders.models import Workorder


def workorder_label(request: WSGIRequest):
    """print a label for a workorder"""
    import_workorders()
    context = {}

    quantity = int(request.GET.get("quantity", 1))
    workorder_id = int(request.GET.get("workorderID", 0))
    if workorder_id == 0:
        context["title"] = "No workorder ID"
        return render(request, "api/error.html", context)
    workorder = Workorder.objects.get(ls_workorder_id=workorder_id)
    workorder.print_label(quantity)
    if str(request.GET.get("manual")).lower() != "true":
        context["auto_close"] = "True"
    return render(request, "api/close_window.html", context)


def ring_central_send_message(request: WSGIRequest):
    """Web listener to generate messages and send them via text"""
    import_workorders()
    context = {}
    ip_address = request.META.get("REMOTE_ADDR")
    if ip_address is None:
        context["title"] = "No IP address"
        return render(request, "api/error.html", context)

    workorder = Workorder.objects.get(ls_workorder_id=int(request.GET.get("workorderID", 0)))
    mobile_number = workorder.customer.mobile_number
    if mobile_number is None:
        context["title"] = "No mobile number"
        return render(request, "api/error.html", context)
    message_number = int(request.GET.get("message", 0))
    workorder.send_rc_message(message_number, ip_address)

    if str(request.GET.get("manual")).lower() != "true":
        context["auto_close"] = "True"

    return render(request, "api/close_window.html", context)
