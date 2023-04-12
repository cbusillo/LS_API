"""Class to import customer objects from LS API"""
import logging
from typing import Any, Generator
from dataclasses import dataclass
from datetime import datetime
from shiny_app.classes.ls_client import Client, string_to_datetime
from shiny_app.modules.load_config import Config


@dataclass
class ContactAddress:
    """Contact Address"""

    def __init__(self, address: dict[str, str]):
        """Load ContactAddress from dict"""
        self.address1 = address.get("address1") or ""
        self.address2 = address.get("address2") or ""
        self.city = address.get("city") or ""
        self.state = address.get("state") or ""
        self.zip = address.get("zip") or ""
        self.country = address.get("country") or ""
        self.country_code = address.get("countryCode") or ""
        self.state_code = address.get("stateCode") or ""


@dataclass
class ContactEmail:
    """Contact email from dict"""

    def __init__(self, email: dict[str, str]):
        """Contact email from dict"""
        self.address = email.get("address") or ""
        self.use_type = email.get("useType") or ""


@dataclass
class ContactPhone:
    """Contact phone"""

    def __init__(self, phone: dict[str, Any]):
        """Contact phone from dict"""
        # if isinstance(obj, dict):
        self.number = phone.get("number") or ""
        self.use_type = phone.get("useType") or ""


@dataclass
class Emails:
    """Email class from LS"""

    def __init__(self, emails: dict[str, Any]):
        """Emails from dict"""

        if emails == "":
            self.contact_emails = []
            return
        contact_emails = emails.get("ContactEmail")
        if isinstance(contact_emails, list):
            self.contact_emails = [ContactEmail(y) for y in contact_emails]
        elif isinstance(contact_emails, dict):
            self.contact_emails = [ContactEmail(contact_emails)]


@dataclass
class Phones:
    """Phones"""

    def __init__(self, phones: dict[str, Any]):
        """Phones from dict"""

        if phones is "":
            self.contact_phones = []
            return
        contact_phones = phones.get("ContactPhone")
        if isinstance(contact_phones, list):
            self.contact_phones = [ContactPhone(y) for y in contact_phones]
        elif isinstance(contact_phones, dict):
            self.contact_phones = [ContactPhone(contact_phones)]


@dataclass
class Addresses:
    """Address class from LS"""

    def __init__(self, address: dict[str, str]):
        """Addresses from dict"""
        contact_address = address.get("ContactAddress")
        if isinstance(contact_address, dict):
            self.contact_address = ContactAddress(contact_address)


@dataclass
class Contact:
    """Contact class from LS"""

    def __init__(self, obj: Any):
        """Contact from LS"""
        self.contact_id = obj.get("contactID") or ""
        self.custom = obj.get("custom") or ""
        self.no_email = obj.get("noEmail") or ""
        self.no_phone = obj.get("noPhone") or ""
        self.no_mail = obj.get("noMail") or ""
        self.addresses = Addresses(obj.get("Addresses"))
        self.phones = Phones(obj.get("Phones"))
        self.emails = Emails(obj.get("Emails"))
        self.websites = obj.get("Websites") or ""
        self.time_stamp = obj.get("timeStamp") or ""


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
        self.customer_id = ls_customer.get("customerID") or 0
        if self.customer_id == 0:
            logging.error("No customer returned from LS (O customer_id)")
            return
        self.first_name = ls_customer.get("firstName").strip() or ""
        self.last_name = ls_customer.get("lastName") or ""
        self.title = ls_customer.get("title") or ""
        self.company = ls_customer.get("company") or ""
        self.create_time = string_to_datetime(ls_customer.get("createTime"))
        self.time_stamp = string_to_datetime(ls_customer.get("timeStamp"))
        self.archived = ls_customer.get("archived").lower() == "true"
        self.contact_id = int(ls_customer.get("contactID"))
        self.credit_account_id = int(ls_customer.get("creditAccountID"))
        self.customer_type_id = int(ls_customer.get("customerTypeID"))
        self.discount_id = int(ls_customer.get("discountID"))
        self.tax_category_id = int(ls_customer.get("taxCategoryID"))
        self.contact = Contact(ls_customer.get("Contact"))
        self.is_modified = False

    def __repr__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def update_phones(self) -> None:
        """call API put to update pricing"""
        if self.contact.phones is None:
            return

        numbers = {}
        for number in self.contact.phones.contact_phones:
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
    def get_customers(cls, customer_id: int = 0, date_filter: datetime | None = None) -> Generator["Customer", None, None]:
        """Generator to return all customers from LS API"""
        if customer_id != 0:
            yield Customer(customer_id=customer_id)
            return
        for customer in cls.client.get_customers_json(date_filter=date_filter):
            yield Customer(ls_customer=customer)
