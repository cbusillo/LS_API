"""Module to clean customer phone numbers."""
import re
import tkinter as tk
from classes import class_customer


def run_update_customer_phone(label: tk.StringVar):
    """Load and iterate through customers, updating formatting on phone numbers."""
    label.set("Running")
    customers = class_customer.Customer.get_customers(label)
    customers_updated = 0
    for index, customer in enumerate(customers):
        if customer.contact.phones:
            for each_number in customer.contact.phones.contact_phone:
                cleaned_number = re.sub(r"[^0-9x]", "", each_number.number)
                if each_number.number != cleaned_number:
                    each_number.number = cleaned_number
                    customer.is_modified = True
                if len(each_number.number) == 7:
                    each_number.number = "757" + each_number.number
                    customer.is_modified = True
        if customer.is_modified:
            customers_updated += 1
            print(f"{customers_updated}: Updating Customer #{index} out of {len(customers): >60}", end="\r")
            label.set(f"{customers_updated}: Updating Customer #{index} out of {len(customers)}")
            customer.update_phones()
