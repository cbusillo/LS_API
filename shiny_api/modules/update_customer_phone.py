"""Module to clean customer phone numbers."""
import os
import re
from kivy.uix.button import Button
from shiny_api.classes import ls_customer

print(f"Importing {os.path.basename(__file__)}...")


def run_update_customer_phone(caller: Button):
    """Load and iterate through customers, updating formatting on phone numbers."""
    customers = ls_customer.Customer.get_customers(caller)
    customers_updated = 0
    for index, customer in enumerate(customers):
        if customer.contact.phones:
            for each_number in customer.contact.phones.contact_phone:
                cleaned_number = re.sub(r"[^0-9x]", "", each_number.number)
                if each_number.number != cleaned_number:
                    each_number.number = cleaned_number
                    customer.is_modified = True
                if len(each_number.number) == 7:
                    each_number.number = f"757{each_number.number}"
                    customer.is_modified = True
        if customer.is_modified:
            customers_updated += 1
            output = f"{customers_updated}: Updating Customer #{index} out of {len(customers): <60}"
            caller.text = f"{caller.text.split(chr(10))[0]}\n{output}"
            print(output, end="\r")
            customer.update_phones(caller)
    caller.disabled = False
    caller.text = caller.text.split("\n")[0]
