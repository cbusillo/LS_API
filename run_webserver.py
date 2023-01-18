"""Run webserver to listen for LS requests."""
from flask import Flask, request

app = Flask(__name__)


@app.route("/webhook", methods=["GET"])
def webhook():
    """Listen for LS"""
    if request.method == "GET":
        print("Data received from Webhook is: ", request.json)


def start_weblistener():
    """Start the listener"""
    app.run(host="0.0.0.0", port=8000)
