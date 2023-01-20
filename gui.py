#!/usr/bin/env python3.11
"""Main GUI File"""
import threading
import tkinter as tk
import customtkinter as ctk  # <- import the CustomTkinter module
from modules import weblistener
from modules import update_item_price
from modules import update_customer_phone
from modules import json_editor
from modules import camera


def update_customer_phone_button_fn():
    """Run the Customer Phone Number Formatting Function"""
    update_customer_phone.run_update_customer_phone(label1)


def update_item_price_button_fn():
    """Run the Item Pricing Function"""
    update_item_price.run_update_item_price(label1)


def open_json_editor_button_fn():
    """Open the price table JSON editor"""
    json_editor.open_json_editor("config/devices.json")


def open_get_serials_button_fn():
    """Open the serial number scanner"""
    camera.take_serial_image()


root_tk = tk.Tk()  # create the Tk window like you normally do
root_tk.geometry("600x400")
root_tk.title("Shiny Computers")
label1 = tk.StringVar()
label1.set("Status")

# Use CTkButton instead of tkinter Button
updateCustomerPhoneButton = ctk.CTkButton(
    master=root_tk,
    corner_radius=10,
    text="Format Customer Phone Numbers",
    command=threading.Thread(target=update_customer_phone_button_fn).start,
)
updateCustomerPhoneButton.pack(pady=20)

updateItemPriceButton = ctk.CTkButton(
    master=root_tk,
    corner_radius=10,
    text="Update iPhone/iPad Prices from Apple and Table",
    command=update_item_price_button_fn,
)
updateItemPriceButton.pack(pady=20)

open_json_editor_button = ctk.CTkButton(
    master=root_tk,
    corner_radius=10,
    text="Edit Price Table",
    command=open_json_editor_button_fn,
)
open_json_editor_button.pack(pady=20)

open_get_serials_button = ctk.CTkButton(
    master=root_tk,
    corner_radius=10,
    text="Load Serial Number Scanner",
    command=open_get_serials_button_fn,
)
open_get_serials_button.pack(pady=20)

line1Label = ctk.CTkLabel(master=root_tk, textvariable=label1)
line1Label.pack(pady=20)

threading.Thread(target=weblistener.start_weblistener).start()

root_tk.mainloop()
