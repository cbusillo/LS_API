"""Zebra printing module"""
import socket


def print_text(text: str):
    """Open socket to printer and send text"""
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "192.168.1.240"
    port = 9100
    mysocket.connect((host, port))  # connecting to host
    mysocket.send(b"^XA^A0N,50,50^FO0,50^FB450,4,,C,^FD" + bytes(text, "utf-8") + b"^FS^XZ")  # using bytes
    mysocket.close()  # closing connection


print_text("Theatrical Builds\&1.18.2023")
