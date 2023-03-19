"""Flask app for API functions"""
import locale
from flask import render_template, request
from shiny_api.classes.ls_workorder import Workorder
from shiny_api.modules.label_print import print_text
import shiny_api.modules.load_config as config
from shiny_api.modules.ring_central import send_message_ssh as send_message


def workorder_label():
    """print a label for a workorder"""
    password = ""
    quantity = int(request.args.get("quantity", 1))
    workorder = Workorder(int(request.args.get("workorderID", 0)))
    for line in workorder.note.split("\n"):
        if line[0:2].lower() == "pw" or line[0:2].lower() == "pc":
            password = line
    print_text(
        f"{workorder.customer.first_name} {workorder.customer.last_name}",
        barcode=f'2500000{workorder.workorder_id}',
        quantity=quantity,
        text_bottom=password,
        print_date=True,
    )
    return render_template('close_window.jinja-html')


def ring_central_send_message():
    """Web listener to generate messages and send them via text"""

    workorder = Workorder(int(request.args.get("workorderID", 0)))
    mobile_number = None

    for phone in workorder.customer.contact.phones.contact_phone:
        if phone.use_type == "Mobile":
            mobile_number = phone.number
    if mobile_number is None:
        return render_template('error.jinja-html')
    message_number = int(request.args.get("message", 0))
    if (
        workorder.total == 0 and request.args.get("message") == "2"
    ):  # if we send a message with price with $0 price
        message_number += 1
    item_description = workorder.item_description
    for word in config.STYLIZED_NAMES:
        if word.lower() in item_description.lower() and word not in item_description:
            index = item_description.lower().find(word.lower())
            item_description = (
                item_description[:index] + word +
                item_description[index + len(word):]
            )

    message = config.RESPONSE_MESSAGES[message_number]
    message = message.format(
        name=workorder.customer.first_name,
        product=item_description,
        total=locale.currency(workorder.total),
    )
    send_message(mobile_number, message)

    return render_template('close_window.jinja-html')
