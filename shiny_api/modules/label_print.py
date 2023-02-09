"""Zebra printing module"""
import datetime
import socket
import os
from typing import List
import zpl
from shiny_api.modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")
LABEL_SIZE = {"width": 36.75, "height": 21}
LABEL_TEXT_SIZE = {"width": 4, "height": 4, "small_width": 2, "small_height": 2}
LABEL_PADDING = 1
BARCODE_HEIGHT = 35


def print_text(text: List[str] = None, barcode: str = None, text_bottom: str = "", quantity: int = 1, print_date: bool = True):
    """Open socket to printer and send text"""
    if not isinstance(text, list):
        text = [text]

    quantity = max(int(quantity), 1)
    label = zpl.Label(width=LABEL_SIZE["width"], height=LABEL_SIZE["height"])
    current_origin = LABEL_PADDING
    for index, line in enumerate(text):
        label.origin(x=0, y=current_origin)
        label.write_text(
            line,
            char_height=LABEL_TEXT_SIZE["width"],
            char_width=LABEL_TEXT_SIZE["height"],
            line_width=LABEL_SIZE["width"],
            justification="C",
        )
        label.endorigin()
        current_origin = (index + 1) * LABEL_TEXT_SIZE["height"] + LABEL_PADDING

    if print_date:
        today = datetime.date.today()
        formatted_date = f"{today.month}.{today.day}.{today.year}"
        label.origin(x=0, y=current_origin)
        label.write_text(
            formatted_date,
            char_height=LABEL_TEXT_SIZE["small_width"],
            char_width=LABEL_TEXT_SIZE["small_height"],
            line_width=LABEL_SIZE["width"],
            justification="C",
        )
        label.endorigin()
        current_origin = current_origin + (LABEL_TEXT_SIZE["small_height"])

    current_origin = LABEL_SIZE["height"] - (BARCODE_HEIGHT / 9) - LABEL_TEXT_SIZE["height"]

    if barcode:
        # 28 = half

        centered_left = 15 - (len(barcode))
        label.origin(x=centered_left, y=current_origin)
        label.barcode(barcode_type="2", code=barcode, height=BARCODE_HEIGHT, magnification=0.2)
        label.endorigin()
        current_origin = current_origin + (BARCODE_HEIGHT / 9) + 2

    if text_bottom:
        label.origin(x=0, y=current_origin)
        label.write_text(
            text_bottom,
            char_height=LABEL_TEXT_SIZE["small_width"],
            char_width=LABEL_TEXT_SIZE["small_height"],
            line_width=LABEL_SIZE["width"],
            justification="C",
        )
        label.endorigin()
    label_text = label.dumpZPL()

    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if socket.gethostname().lower() is not False:  # "chris-mbp":
        mysocket.connect((config.PRINTER_HOST, config.PRINTER_PORT))  # connecting to host
        for _ in range(quantity):
            mysocket.send(bytes(label_text, "utf-8"))  # using bytes
        mysocket.close()  # closing connection
