"""webview to print labels"""
from flask import render_template, request
from pydantic import BaseModel
import shiny_api.modules.load_config as config
from shiny_api.modules.label_print import print_text


class LabelGroup(BaseModel):
    """Class to hold label group data"""

    name: str
    labels: list[str]
    printer_ip: str

    @staticmethod
    def load_from_defaults():
        """Load label groups from config.DEFAULT_LABELS"""
        return {name: LabelGroup(name=name, labels=label_group["labels"], printer_ip=label_group["printer_ip"])
                for name, label_group in config.DEFAULT_LABELS.items()}


def label_printer_view(active_label_group: str = "Main Labels"):
    """View to print labels"""
    label_group_list: dict[LabelGroup] = LabelGroup.load_from_defaults()
    label_group_name_list = [label_group_name for label_group_name in label_group_list.keys()]
    quantity = int(request.form.get("quantity", 1))
    label_text = ""
    page_error = ""

    if bool(request.form.get("custom_label_print", False)):
        label_text = request.form.get("custom_label_text", "")
    else:
        label_text = label_text or request.form.get("label_text", "")
    lines = label_text.split("\n")
    while "" in lines:
        lines.remove("")
    label_text = lines
    if label_text == "" or quantity < 1:
        page_error = "No label text"
    else:
        print(f"Printing {label_text} to {request.form.get('printer', '')}...")
        try:
            print_text(quantity=quantity,
                       barcode=request.form.get("barcode", ""),
                       print_date=bool(request.form.get("date", False)),
                       text=label_text)
        except TimeoutError as error:
            page_error = error

    return render_template('labels.html',
                           title="Label Printer",
                           label_group_name_list=label_group_name_list,
                           active_labels=label_group_list[active_label_group].labels,
                           active_label_group=active_label_group,
                           error=page_error,
                           )
