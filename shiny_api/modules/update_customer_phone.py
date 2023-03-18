"""Module to clean customer phone numbers."""
import os
import re
from shiny_api.classes import ls_customer
from shiny_api.views.ls_functions import send_message

print(f"Importing {os.path.basename(__file__)}...")


def format_customer_phone():
    """Load and iterate through customers, updating formatting on phone numbers."""
    customers = ls_customer.Customers()
    customers_updated = 0
    for index, customer in enumerate(customers.customer_list):
        if len(customer.contact.phones.contact_phone) == 0:
            continue
        has_mobile = False
        for each_number in customer.contact.phones.contact_phone:
            cleaned_number = re.sub(r"[^0-9x]", "", each_number.number)

            if each_number.number != cleaned_number:
                each_number.number = cleaned_number
                customer.is_modified = True
            if len(each_number.number) == 7:
                each_number.number = f"757{each_number.number}"
                customer.is_modified = True
            if len(each_number.number) == 11:
                each_number.number = each_number.number[1:]
                customer.is_modified = True
            if each_number.use_type == "Mobile":
                has_mobile = True
        if customer.is_modified or has_mobile is False:
            customers_updated += 1
            output = (
                f"{customers_updated}: Updating Customer #{index}"
                f" out of {len(customers.customer_list): <60}")
            send_message(output)
            print(output, end="\r")
            customer.update_phones()
