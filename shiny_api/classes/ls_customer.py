"""Class to import customer objects from LS API"""
import os
from typing import Any
from dataclasses import dataclass
from kivy.uix.button import Button
from shiny_api.modules.connect_ls import generate_ls_access, get_data, put_data
from shiny_api.modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")


@dataclass
class ContactAddress:
    """Contact Address"""

    def __init__(self, obj: Any):
        """Load ContactAddress from dict"""
        self.address1 = str(obj.get("address1"))
        self.address2 = str(obj.get("address2"))
        self.city = str(obj.get("city"))
        self.state = str(obj.get("state"))
        self.zip = str(obj.get("zip"))
        self.country = str(obj.get("country"))
        self.country_code = str(obj.get("countryCode"))
        self.state_code = str(obj.get("stateCode"))


@dataclass
class ContactEmail:
    """Contact email from dict"""

    def __init__(self, obj: Any):
        """Contact email from dict"""
        if isinstance(obj, list):
            self.address = str(obj.get("address"))
            self.use_type = str(obj.get("useType"))


@dataclass
class ContactPhone:
    """Contact phone"""

    def __init__(self, obj: Any):
        """Contact phone from dict"""
        # if isinstance(obj, dict):
        self.number = str(obj.get("number"))
        self.use_type = str(obj.get("useType"))


@dataclass
class Emails:
    """Email class from LS"""

    def __init__(self, obj: Any):
        """Emails from dict"""
        if obj:
            self.contact_email: list[ContactEmail] = [ContactEmail(y) for y in obj.get("ContactEmail")]


@dataclass
class Phones:
    """Phones"""

    def __init__(self, obj: Any):
        """Phones from dict"""
        if obj == "":
            self.contact_phone = []
            return
        if isinstance(obj.get("ContactPhone"), list):
            self.contact_phone = [ContactPhone(y) for y in obj.get("ContactPhone")]
        else:
            self.contact_phone = [ContactPhone(obj.get("ContactPhone"))]


@dataclass
class Addresses:
    """Address class from LS"""

    def __init__(self, obj: Any):
        """Addresses from dict"""
        self.contact_address = ContactAddress(obj.get("ContactAddress"))


@dataclass
class Contact:
    """Contact class from LS"""

    def __init__(self, obj: Any):
        """Contact from LS"""
        self.contact_id = str(obj.get("contactID"))
        self.custom = str(obj.get("custom"))
        self.no_email = str(obj.get("noEmail"))
        self.no_phone = str(obj.get("noPhone"))
        self.no_mail = str(obj.get("noMail"))
        self.addresses = Addresses(obj.get("Addresses"))
        self.phones = Phones(obj.get("Phones"))
        self.emails = Emails(obj.get("Emails"))
        self.websites = str(obj.get("Websites"))
        self.time_stamp = str(obj.get("timeStamp"))


@dataclass
class Customer:
    """Customer object from LS"""

    def __init__(self, customer_id: int = None, ls_customer: Any = None):
        """Customer object from dict"""
        if ls_customer is None:
            if customer_id is None:
                raise ValueError("Customer ID or LS Customer object required")
            self.customer_id = customer_id
            ls_customer = self._get_customer()
        self.customer_id = ls_customer.get("customerID")

        self.first_name = str(ls_customer.get("firstName")).strip()
        self.last_name = str(ls_customer.get("lastName"))
        self.title = str(ls_customer.get("title"))
        self.company = str(ls_customer.get("company"))
        self.create_time = str(ls_customer.get("createTime"))
        self.time_stamp = str(ls_customer.get("timeStamp"))
        self.archived = str(ls_customer.get("archived"))
        self.contact_id = str(ls_customer.get("contactID"))
        self.credit_account_id = str(ls_customer.get("creditAccountID"))
        self.customer_type_id = str(ls_customer.get("customerTypeID"))
        self.discount_id = str(ls_customer.get("discountID"))
        self.tax_category_id = str(ls_customer.get("taxCategoryID"))
        self.contact = Contact(ls_customer.get("Contact"))
        self.is_modified = False

    def __repr__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def _get_customer(self):
        """Get single customer from LS API into Customer object"""
        generate_ls_access()
        response = get_data(config.LS_URLS["customer"].format(customerID=self.customer_id), {"load_relations": '["Contact"]'})

        return response.json().get("Customer")

    def update_phones(self, caller: Button = None):
        """call API put to update pricing"""
        if self.contact.phones is None:
            return

        numbers = {}
        for number in self.contact.phones.contact_phone:
            numbers[number.use_type] = number.number

        numbers["Mobile"] = (
            numbers.get("Mobile") or numbers.get("Home") or numbers.get("Work") or numbers.get("Fax") or numbers.get("Pager")
        )
        values = {value: key for key, value in numbers.items()}
        numbers = {value: key for key, value in values.items()}

        put_customer = {
            "Contact": {
                "Phones": {
                    "ContactPhone": [
                        {"number": f"{numbers.get('Mobile') or ''}", "useType": "Mobile"},
                        {"number": f"{numbers.get('Fax') or ''}", "useType": "Fax"},
                        {"number": f"{numbers.get('Pager') or ''}", "useType": "Pager"},
                        {"number": f"{numbers.get('Work') or ''}", "useType": "Work"},
                        {"number": f"{numbers.get('Home') or ''}", "useType": "Home"},
                    ]
                }
            }
        }
        put_data(config.LS_URLS["customer"].format(customerID=self.customer_id), put_customer, caller)


@dataclass
class Customers:
    """Return list of Customers"""

    def __init__(self, caller: Button = None):
        """List of customers"""
        self.customer_list: list[Customers] = []
        self._get_customers(caller)

    def _get_customers(self, caller: Button = None):
        """API call to get all items.  Walk through categories and pages.
        Convert from json dict to Item object and add to itemList list."""
        # Run API auth
        generate_ls_access()

        current_url = config.LS_URLS["customers"]
        pages = 0
        while current_url:
            response = get_data(current_url, {"load_relations": '["Contact"]', "limit": 100}, caller)
            for customer in response.json().get("Customer"):
                self.customer_list.append(Customer(ls_customer=customer))
            current_url = response.json()["@attributes"]["next"]

            pages += 1
            output = f"Loading page: {pages}"
            if caller:
                caller.text = f"{caller.text.split(chr(10))[0]}\n{output}"
            print(f"{output: <100}", end="\r")
        print()

    def __repr__(self) -> str:
        return f"{len(self)} customers"


if __name__ == "__main__":
    test = Customers()
    print(test)
