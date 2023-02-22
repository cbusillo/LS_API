"""Zebra printing module"""
import datetime
import os
from typing import List
from simple_zpl2 import ZPLDocument, Code128_Barcode, NetworkPrinter
from shiny_api.modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")
LABEL_SIZE = {"width": 2, "height": 1.3}
LABEL_TEXT_SIZE = {"width": 40, "height": 40, "small_width": 20, "small_height": 20}
LABEL_PADDING = 10
BARCODE_HEIGHT = 35


def print_text(
    text: List[str] = None,
    barcode: str = None,
    text_bottom: str = None,
    quantity: int = 1,
    print_date: bool = True,
    printer_ip: str = config.PRINTER_HOST,
):
    """Open socket to printer and send text"""
    if not isinstance(text, list):
        text = [text]

    label_width = int(203 * LABEL_SIZE["width"])
    label_height = int(203 * LABEL_SIZE["height"])

    quantity = max(int(quantity), 1)
    label = ZPLDocument()
    label.add_zpl_raw("^BY2")
    label.add_default_font(font_name=0, character_height=LABEL_TEXT_SIZE["height"], character_width=LABEL_TEXT_SIZE["width"])
    current_origin = LABEL_PADDING
    for index, line in enumerate(text):
        label.add_field_block(text_justification="C", width=label_width)
        label.add_field_origin(x_pos=LABEL_PADDING, y_pos=current_origin, justification=2)
        label.add_field_data(line)
        current_origin = (index + 1) * LABEL_TEXT_SIZE["height"] + LABEL_PADDING

    if print_date:
        today = datetime.date.today()
        formatted_date = f"{today.month}.{today.day}.{today.year}"
        label.add_default_font(
            font_name=0, character_height=LABEL_TEXT_SIZE["small_height"], character_width=LABEL_TEXT_SIZE["small_width"]
        )
        label.add_field_block(text_justification="C", width=label_width)
        label.add_field_origin(x_pos=LABEL_PADDING, y_pos=current_origin, justification=2)
        label.add_field_data(formatted_date)
        current_origin = current_origin + (LABEL_TEXT_SIZE["small_height"])

    if text_bottom:
        label.add_field_block(text_justification="C", width=label_width)
        label.add_field_origin(x_pos=LABEL_PADDING, y_pos=current_origin, justification=2)
        label.add_field_data(text_bottom)

    current_origin = int(label_height - (BARCODE_HEIGHT * 2))

    if barcode:
        centered_left = 194 - int(((len(barcode) * 21) + 75) / 2)
        barcode_zpl = Code128_Barcode(barcode, "N", BARCODE_HEIGHT, "Y", "N")

        label.add_field_block(width=label_width)
        label.add_field_origin(x_pos=LABEL_PADDING + centered_left, y_pos=current_origin, justification=2)
        label.add_barcode(barcode_zpl)
        current_origin = current_origin + (BARCODE_HEIGHT / 9) + 2

    printer = NetworkPrinter(printer_ip)
    for _ in range(quantity):
        printer.print_zpl(label)
