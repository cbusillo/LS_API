"""webview to print labels"""
import time
from flask import render_template, request
from flask_sse import sse
from threading import Thread
from shiny_api.modules.flask_server import app

current_session = None


def ls_functions_view():
    print("staring message")
    sse.publish({"message": "start!"}, type='update')
    app.session = request.cookies.get('session')
    thread = Thread(target=send_message)
    thread.daemon = True
    thread.start()
    return render_template('ls_functions.html',
                           title="Light Speed Functions",
                           )


def send_message():

    print("Sending message")
    with app.app_context():
        for count in range(10):
            time.sleep(1)
            sse.publish({"message": f"sent {count}!"}, type='update', channel=app.session)
            print(f"sent {count}!")
