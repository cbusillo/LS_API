"""Run webserver to listen for LS requests."""
import os
import datetime
from flask import Flask, request
from kivy.uix.button import Button
from shiny_api.classes import ls_customer
from shiny_api.classes import ls_workorder
from shiny_api.modules import label_print

print(f"Importing {os.path.basename(__file__)}...")

app = Flask(__name__)

HTML_RETURN = """<html><script type="text/javascript">
open(location, '_self').close(); 
</script>
<a id='close_button' href="javascript:window.open('','_self').close();">Close Tab</a></html>"""


@app.route("/wo_label", methods=["GET"])
def web_hd_label():
    """Print customer HDD label"""
    quantity = 0
    password = ""
    if request.args.get("quantity") is None:
        quantity = 1
    else:
        quantity = int(request.args.get("quantity"))
    customer = ls_customer.Customer.get_customer(request.args.get("customerID"))
    today = datetime.date.today()
    workorder = ls_workorder.Workorder.get_workorder(request.args.get("workorderID"))
    for line in workorder.note.split("\n"):
        if line[0:2].lower() == "pw" or line[0:2].lower() == "pc":
            password = line
    print(password)
    print(f"{customer.first_name} {customer.last_name}")
    print(f"{today.month}.{today.day}.{today.year}")
    print(workorder.note)
    label_print.print_text(
        f"{customer.first_name} {customer.last_name}",
        barcode=f'2500000{request.args.get("workorderID")}',
        quantity=quantity,
        text_bottom=password,
        print_date=True,
    )
    return HTML_RETURN


def start_weblistener(caller: Button):
    """Start the listener"""
    caller.text = f"{caller.text.split(chr(10))[0]}\nListner Started"
    app.run(host="0.0.0.0", port=8000)
    caller.disabled = False
    caller.text = caller.text.split("\n")[0]
