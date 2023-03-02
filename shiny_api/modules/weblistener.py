"""Run webserver to listen for LS requests."""
import os
import datetime
import locale
from flask import Flask, request
from kivy.uix.button import Button
from shiny_api.classes import ls_customer
from shiny_api.classes import ls_workorder
from shiny_api.modules import label_print
import shiny_api.modules.ring_central as ring_central
import shiny_api.modules.load_config as config

print(f"Importing {os.path.basename(__file__)}...")

app = Flask(__name__)

HTML_RETURN = """<html><script type="text/javascript">
open(location, '_self').close(); 
</script>
<a id='close_button' href="javascript:window.open('','_self').close();">Close Tab</a></html>"""
HTML_ERROR = "<html>No mobile phone number (Maybe run format customer phone numbers)<br><br>{error}</html>"

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")


@app.route("/wo_label", methods=["GET"])
def web_hd_label():
    """Print customer HDD label"""
    password = ""
    if request.args.get("quantity") is None:
        quantity = 1
    else:
        quantity = int(request.args.get("quantity"))
    customer = ls_customer.Customer.get_customer(request.args.get("customerID"))
    today = datetime.date.today()
    workorder = ls_workorder.Workorder(request.args.get("workorderID"))
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


@app.route("/rc_send_message", methods=["GET"])
def rc_send_message():
    """Web listener to generate messages and send them via text"""
    customer = ls_customer.Customer.get_customer(request.args.get("customerID"))
    workorder = ls_workorder.Workorder(request.args.get("workorderID"))
    for phone in customer.contact.phones.contact_phone:
        if phone.use_type == "Mobile":
            phone_number = phone.number
    try:
        if phone_number is None:
            return HTML_RETURN
    except UnboundLocalError as error:
        return HTML_ERROR.format(error=error)
    message_number = int(request.args.get("message"))
    if workorder.total == 0 and request.args.get("message") == "2":  # if we send a message with price with $0 price
        message_number += 1
    item_description = workorder.item_description
    for word in config.STYLIZED_NAMES:
        if word.lower() in item_description.lower() and word not in item_description:
            index = item_description.lower().find(word.lower())
            item_description = item_description[:index] + word + item_description[index + len(word) :]

    message = config.RESPONSE_MESSAGES[message_number]
    message = message.format(name=customer.first_name, product=item_description, total=locale.currency(workorder.total))
    # message = message.replace("{{product}}", workorder)
    ring_central.send_message(phone_number, message)

    return HTML_RETURN


def start_weblistener(caller: Button):
    """Start the listener"""
    caller.text = f"{caller.text.split(chr(10))[0]}\nListner Started"
    from waitress import serve

    serve(app, host="0.0.0.0", port=8000)
    caller.disabled = False
    caller.text = caller.text.split("\n")[0]
