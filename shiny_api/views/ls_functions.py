"""webview to print labels"""
from threading import Thread
from typing import Callable
from importlib import import_module

from flask import render_template, redirect, url_for
from flask_sse import sse

from shiny_api.modules.flask_server import app


def ls_functions_view(module_function_name: str = ""):
    """View for Light Speed Functions"""
    buttons = {
        "shiny_api.modules.update_customer_phone|format_customer_phone":
            "Format Customer Phone Numbers",
        "shiny_api.modules.update_item_price|update_item_price":
            "Update iPhone/iPad Prices",

    }

    if module_function_name == "" or app.running_function.get(module_function_name, False):
        return render_template(
            'ls_functions.html',
            title="Light Speed Functions",
            buttons=buttons
        )

    print("staring message")
    sse.publish({"message": "start!"}, type='update')

    module_name, function_name = module_function_name.split("|")

    module = import_module(module_name)
    function_to_exec = getattr(module, function_name)
    thread = Thread(target=run_function, args=[function_to_exec, module_function_name])
    thread.daemon = True
    app.running_function[module_function_name] = True
    print(thread.start())
    return redirect(url_for('ls_functions_view'))


def run_function(function_to_exec: Callable, module_function_name, status: str = ""):
    """End function"""
    print("Function finished")
    with app.app_context():
        function_to_exec()
        app.running_function[module_function_name] = False
        sse.publish({"message": f"{status}Finished!"}, type='update')


def send_message(message) -> None:
    """Pass SSE message to browser"""
    if app is None:
        return
    sse.publish({"message": message}, type='status')
