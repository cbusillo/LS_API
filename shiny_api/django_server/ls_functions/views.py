"""View for LS Functions"""
from importlib import import_module
from threading import Thread
from asgiref.sync import async_to_sync
from channels_redis.core import RedisChannelLayer  # type: ignore
from channels.layers import get_channel_layer  # type: ignore
from django.core.handlers.wsgi import WSGIRequest  # type: ignore
from django.shortcuts import render, redirect  # type: ignore

# from django_eventstream import send_event
from shiny_api.django_server.settings import running_function


def ls_functions(request: WSGIRequest, module_function_name: str = ""):
    """View for Light Speed Functions"""
    buttons = {
        "shiny_api.modules.light_speed|format_customer_phone": "Format Customer Phone Numbers",
        "shiny_api.modules.light_speed|update_item_price": "Update iPhone/iPad Prices",
    }
    context: dict[str, object] = {}
    context["title"] = "Light Speed Functions"

    if module_function_name == "" or running_function.get(module_function_name, False):
        context["buttons"] = buttons
        return render(request, "ls_functions.django-html", context)

    module_name, function_name = module_function_name.split("|")

    module = import_module(module_name)
    function_to_exec = getattr(module, function_name)
    thread = Thread(target=run_function, args=[function_to_exec, module_function_name])
    thread.daemon = True
    running_function[module_function_name] = True
    thread.start()
    return redirect(ls_functions)


def run_function(function_to_exec, module_function_name):
    """End function"""
    channel_layer = get_channel_layer()
    if not isinstance(channel_layer, RedisChannelLayer):
        return
    async_to_sync(channel_layer.group_send)(
        "updates",
        {
            "type": "status",
            "message": f"starting {module_function_name}.{function_to_exec}",
        },
    )
    function_to_exec()
    running_function[module_function_name] = False
    #     sse.publish({"message": f"{status}Finished!"}, type='status')


def send_message(message: str) -> None:
    """Pass Event message to browser"""
    channel_layer = get_channel_layer()
    if not isinstance(channel_layer, RedisChannelLayer):
        return
    async_to_sync(channel_layer.group_send)(
        "updates", {"type": "status", "message": message}
    )

    # if app is None:
    #     return
    # with app.app_context():
    #     sse.publish({"message": message}, type='status')
