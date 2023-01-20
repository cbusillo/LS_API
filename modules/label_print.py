"""Zebra printing module"""
import socket
import os

print(f"Importing {os.path.basename(__file__)}...")


def print_text(text: str, barcode=None, qty=1):
    """Open socket to printer and send text"""
    label_string = b"^XA^A0N,50,50^FO0,50^FB450,4,,C,^FD" + bytes(text, "utf-8")
    if barcode:
        label_string += b"^B3N,N,100,Y,N" + bytes(barcode, "utf-8")
    label_string += b"^FS^XZ"

    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "192.168.1.240"
    port = 9100
    if socket.gethostname().lower() != "chris-mbp":
        mysocket.connect((host, port))  # connecting to host
        for _ in range(qty):
            mysocket.send(label_string)  # using bytes
        mysocket.close()  # closing connection
