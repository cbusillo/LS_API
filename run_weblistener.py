"""Run webserver to listen for LS requests."""
import datetime
from flask import Flask, request
from modules import class_customer
from modules import label_print


app = Flask(__name__)


@app.route("/hdd_label", methods=["GET"])
def web_hd_label():
    """Print customer HDD label"""
    if request.method == "GET":
        customer = class_customer.Customer.get_customer(request.args.get("customerID"))
        today = datetime.date.today()
        print(f"{customer.first_name} {customer.last_name}")
        print(f"{today.month}.{today.day}.{today.year}")
        label_print.print_text(f"{customer.first_name} {customer.last_name}\n{today.month}.{today.day}.{today.year}")
    return "<html></html>"


def start_weblistener():
    """Start the listener"""
    app.run(host="0.0.0.0", port=8000)


start_weblistener()
