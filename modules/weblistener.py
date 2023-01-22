"""Run webserver to listen for LS requests."""
import os
import datetime
from flask import Flask, request
from classes import ls_customer
from modules import label_print

print(f"Importing {os.path.basename(__file__)}...")

app = Flask(__name__)

HTML_RETURN = """<html><script type="text/javascript">
open(location, '_self').close(); 
</script>
<a id='close_button' href="javascript:window.open('','_self').close();">Close Tab</a></html>"""


@app.route("/hdd_label", methods=["GET"])
def web_hd_label():
    """Print customer HDD label"""

    customer = ls_customer.Customer.get_customer(request.args.get("customerID"))
    today = datetime.date.today()
    print(f"{customer.first_name} {customer.last_name}")
    print(f"{today.month}.{today.day}.{today.year}")
    label_print.print_text(
        f"{customer.first_name} {customer.last_name}\\&{today.month}.{today.day}.{today.year}"
    )
    return HTML_RETURN


@app.route("/in_process_label", methods=["GET"])
def web_in_process_label():
    """Print customer name and workorder number barcode to label printer"""
    customer = ls_customer.Customer.get_customer(request.args.get("customerID"))
    today = datetime.date.today()
    print(f"{customer.first_name} {customer.last_name}")
    label_print.print_text(
        f"{customer.first_name} {customer.last_name}\\&{today.month}.{today.day}.{today.year}",
        barcode="2500000" + request.args.get("workorderID"),
        quantity=request.args.get("qty"),
    )
    return HTML_RETURN


def start_weblistener():
    """Start the listener"""
    app.run(host="0.0.0.0", port=8000)
