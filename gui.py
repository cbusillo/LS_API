#!/usr/bin/env python3.11
"""Main GUI File"""
import threading
import tkinter as tk
import customtkinter as ctk  # <- import the CustomTkinter module
from modules import weblistener
import modules.update_item_price as update_item_price
import modules.update_customer_phone as update_customer_phone


def update_customer_phone_button_fn():
    """Run the Customer Phone Number Formatting Function"""
    update_customer_phone.run_update_customer_phone(label1)


def update_item_price_button_fn():
    """Run the Item Pricing Function"""
    update_item_price.run_update_item_price(label1)


def update_item_price_table_button_fn():
    """Open the price table JSON editor"""


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

updateItemPriceTableButton = ctk.CTkButton(
    master=root_tk,
    corner_radius=10,
    text="Edit Price Table",
    command=update_item_price_table_button_fn,
)
updateItemPriceTableButton.pack(pady=20)

line1Label = ctk.CTkLabel(master=root_tk, textvariable=label1)
line1Label.pack(pady=20)

threading.Thread(target=weblistener.start_weblistener).start()

root_tk.mainloop()
