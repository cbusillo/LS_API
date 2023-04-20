"""View for LS Functions"""
import logging
from importlib import import_module
from threading import Thread
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels_redis.core import RedisChannelLayer
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render

# from django_eventstream import send_event
from shiny_app.django_server.settings import running_functions


def home(request: WSGIRequest, module_function_name: str = ""):
    """View for Light Speed Functions"""
    buttons = {
        "shiny_app.django_server.customers.models|format_customer_phone": "Format Customer Phone Numbers",
        "shiny_app.modules.light_speed|update_item_price": "Update iPhone/iPad Prices",
        "shiny_app.modules.light_speed|import_items": "Import Items",
        "shiny_app.modules.light_speed|import_customers": "Import Customers",
        "shiny_app.modules.light_speed|import_workorders": "Import Workorders",
        "shiny_app.modules.light_speed|import_all": "Import All",
        "shiny_app.modules.light_speed|delete_all": "Delete All",
        "shiny_app.modules.scroll|run": "Scroll",
        "shiny_app.django_server.functions.views|reset_running_functions": "Reset Running Functions",
    }
    context: dict[str, object] = {}
    context["title"] = "Light Speed Functions"

    if module_function_name == "" or running_functions.get(module_function_name, False):
        context["buttons"] = buttons
        return render(request, "functions/home.html", context)

    module_name, function_name = module_function_name.split("|")

    module = import_module(module_name)
    function_to_exec = getattr(module, function_name)
    thread = Thread(target=run_function, args=[function_to_exec, module_function_name])
    thread.daemon = True
    running_functions[module_function_name] = True
    thread.start()
    return redirect("functions:home")


def run_function(function_to_exec, module_function_name):
    """End function"""
    channel_layer = get_channel_layer()
    if not isinstance(channel_layer, RedisChannelLayer):
        return
    send_message(f"starting {module_function_name}.{function_to_exec}")
    function_to_exec()
    running_functions[module_function_name] = False
    #     sse.publish({"message": f"{status}Finished!"}, type='status')


def send_message(message: str) -> None:
    """Pass Event message to browser"""
    channel_layer = get_channel_layer()
    if not isinstance(channel_layer, RedisChannelLayer):
        return
    message = f"{datetime.now().strftime('%H:%M:%S')} - {message}"
    async_to_sync(channel_layer.group_send)("updates", {"type": "status", "message": message})
    logging.info("updates channel message: %s", message)


def reset_running_functions():
    """Reset running function"""
    running_functions.clear()
