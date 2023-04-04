"""Class to import customer objects from LS API"""
from typing import Any
from dataclasses import dataclass
from datetime import datetime
from rich import print as pprint
from shiny_api.classes.ls_client import Client
from shiny_api.modules.load_config import Config


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

    def __init__(self, obj: dict["str", "str"]):
        """Contact email from dict"""
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
        if obj == "":
            self.contact_email = []
            return
        if isinstance(obj.get("ContactEmail"), list):
            self.contact_email = [ContactEmail(y) for y in obj.get("ContactEmail")]
        else:
            self.contact_email = [ContactEmail(obj.get("ContactEmail"))]


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

    client = Client()

    def __init__(self, customer_id: int = 0, ls_customer: Any = None):
        """Customer object from dict"""
        if ls_customer is None:
            if customer_id == 0:
                raise ValueError("Customer ID or LS Customer object required")
            self.customer_id = customer_id
            ls_customer = self.client.get_customer_json(self.customer_id)
        self.customer_id = ls_customer.get("customerID")

        self.first_name = str(ls_customer.get("firstName")).strip()
        self.last_name = str(ls_customer.get("lastName"))
        self.title = str(ls_customer.get("title"))
        self.company = str(ls_customer.get("company"))
        self.create_time = str(ls_customer.get("createTime"))
        self.time_stamp = str(ls_customer.get("timeStamp"))
        self.archived = bool(ls_customer.get("archived").lower() == "true")
        self.contact_id = str(ls_customer.get("contactID"))
        self.credit_account_id = str(ls_customer.get("creditAccountID"))
        self.customer_type_id = str(ls_customer.get("customerTypeID"))
        self.discount_id = str(ls_customer.get("discountID"))
        self.tax_category_id = str(ls_customer.get("taxCategoryID"))
        self.contact = Contact(ls_customer.get("Contact"))
        self.is_modified = False

    def __repr__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def update_phones(self):
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
        url = Config.LS_URLS["customer"].format(customerID=self.customer_id)
        self.client.put(url, json=put_customer)

    @classmethod
    def get_customers(cls, customer_id: int = 0, date_filter: datetime | None = None):
        """Generator to return all customers from LS API"""
        if customer_id != 0:
            yield Customer(customer_id=customer_id)
            return
        for customer in cls.client.get_customers_json(date_filter=date_filter):
            yield Customer(ls_customer=customer)


if __name__ == "__main__":
    test = Customer.get_customers()
    for x in test:
        pprint(x)
