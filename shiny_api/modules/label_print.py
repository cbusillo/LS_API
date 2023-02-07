"""Zebra printing module"""
import socket
import os
from shiny_api.modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")


def print_text(text: str, barcode=None, quantity=None, text_bottom=None):
    """Open socket to printer and send text"""
    label_string = b"^XA^A0N,50,50^FO0,20^FB450,4,,C,^FD" + bytes(text, "utf-8")
    if barcode:
        label_string += b"^FS^FO40,130^FB450,4,,C,^B2N,40,Y,N,N^FD" + bytes(barcode, "utf-8")
    if text_bottom:
        label_string += b"^FS^A0N,30,30^FO0,210^FB450,4,,C,^FD" + bytes(text_bottom, "utf-8")
    label_string += b"^FS^XZ"
    if quantity is None:
        quantity = 1
    quantity = int(quantity)
    if quantity < 1:
        quantity = 1

    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if socket.gethostname().lower() is not False:  # "chris-mbp":
        mysocket.connect((config.PRINTER_HOST, config.PRINTER_PORT))  # connecting to host
        for _ in range(quantity):
            mysocket.send(label_string)  # using bytes
        mysocket.close()  # closing connection
