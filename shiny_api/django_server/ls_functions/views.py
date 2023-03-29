"""View for LS Functions"""
from importlib import import_module
from threading import Thread
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
# from django_eventstream import send_event
from shiny_api.django_server.settings import running_function


def ls_functions(request: WSGIRequest, module_function_name: str = ""):
    """View for Light Speed Functions"""
    buttons = {
        "shiny_api.modules.light_speed|format_customer_phone":
            "Format Customer Phone Numbers",
        "shiny_api.modules.light_speed|update_item_price":
            "Update iPhone/iPad Prices",

    }
    context = {}
    context["title"] = "Light Speed Functions"

    if module_function_name == "" or running_function.get(module_function_name, False):

        context["buttons"] = buttons
        return render(request, 'ls_functions.django-html', context)

    print("starting message")
    # send_event('update', 'message', {'text': 'Start!'})

    module_name, function_name = module_function_name.split("|")

    module = import_module(module_name)
    function_to_exec = getattr(module, function_name)
    thread = Thread(target=run_function, args=[function_to_exec, module_function_name])
    thread.daemon = True
    running_function[module_function_name] = True
    print(thread.start())
    return redirect(ls_functions)


def run_function(function_to_exec, module_function_name, status: str = ""):
    """End function"""
    # with app.app_context():
    function_to_exec()
    running_function[module_function_name] = False
    #     sse.publish({"message": f"{status}Finished!"}, type='status')


def send_message(message) -> None:
    """Pass SSE message to browser"""
    # if app is None:
    #     return
    # with app.app_context():
    #     sse.publish({"message": message}, type='status')
