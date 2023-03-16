import locale
import os
from django.shortcuts import render

from shiny_api.classes.ls_customer import Customer
from shiny_api.classes.ls_workorder import Workorder
from shiny_api.modules.label_print import print_text
import shiny_api.modules.ring_central as ring_central
import shiny_api.modules.load_config as config
from shiny_api.classes.label_group import LabelGroup

print(f"Importing {os.path.basename(__file__)}...")


def index(request, label_group: str = "Main Labels"):
    label_group_list: dict[LabelGroup] = LabelGroup.load_from_defaults()
    quantity = request.POST.get("quantity", 1)
    context = {}
    context["label_lists"] = [label_group for label_group in label_group_list.keys()]
    context["labels"] = label_group_list[label_group].labels
    context["title"] = "Label Printer"
    context["active_label_list"] = label_group
    label_text = ""
    if bool(request.POST.get("custom_label_print", False)):
        label_text = request.POST.get("custom_label_text", "")
    else:
        label_text = label_text or request.POST.get("label_text", "")

    if label_text == "" or quantity < 1:
        context["error"] = "No label text"
        return render(request, 'index.html', context=context)
    print(f"Printing {label_text} to {request.POST.get('printer', '')}...")
    try:
        print_text(quantity=quantity,
                   barcode=request.POST.get("barcode", ""),
                   print_date=bool(request.POST.get("date", False)),
                   text=label_text)
    except TimeoutError as error:
        context["error"] = error

    return render(request, 'index.html', context=context)


def about(request):

    return render(request, 'about.html')

# localhost:8000/label_printer/api/?quantity=4&workorderID=25644&customerID=15762


def workorder_label(request):
    password = ""
    quantity = int(request.GET.get("quantity", 1))
    customer = Customer(int(request.GET.get("customerID", 0)))
    workorder = Workorder(int(request.GET.get("workorderID", 0)))
    for line in workorder.note.split("\n"):
        if line[0:2].lower() == "pw" or line[0:2].lower() == "pc":
            password = line
    print_text(
        f"{customer.first_name} {customer.last_name}",
        barcode=f'2500000{workorder.workorder_id}',
        quantity=quantity,
        text_bottom=password,
        print_date=True,
    )
    return render(request, 'close_window.html')


def ring_central_send_message(request):
    """Web listener to generate messages and send them via text"""
    customer = Customer(int(request.args.get("customerID", 0)))
    workorder = Workorder(int(request.args.get("workorderID", 0)))
    mobile_number = None

    for phone in customer.contact.phones.contact_phone:
        if phone.use_type == "Mobile":
            mobile_number = phone.number
    if mobile_number is None:
        return render(request, 'error.html')
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
        name=customer.first_name,
        product=item_description,
        total=locale.currency(workorder.total),
    )
    ring_central.send_message(mobile_number, message)

    return render(request, 'close_window.html')
