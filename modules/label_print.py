"""Zebra printing module"""
import socket


def print_text(text: str):
    """Open socket to printer and send text"""
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "192.168.1.240"
    port = 9100
    mysocket.connect((host, port))  # connecting to host
    mysocket.send(b"^XA^A0N,50,50^FO50,50^FD" + text + b"^FS^XZ")  # using bytes
    mysocket.close()  # closing connection
