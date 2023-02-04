"""Class to import customer objects from LS API"""
import os
import json
from typing import List, Any
from dataclasses import dataclass
from kivy.uix.button import Button
from shiny_api.modules.connect_ls import generate_ls_access, get_data, put_data
from shiny_api.modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")


def to_json(tojson):
    """convert string to JSON"""
    return json.dumps(
        tojson,
        default=lambda o: o.__dict__,
        sort_keys=True,
        indent=None,
        separators=(", ", ": "),
    )


@dataclass
class ContactAddress:
    """Contact Address"""

    address1: str
    address2: str
    city: str
    state: str
    zip: str
    country: str
    country_code: str
    state_code: str

    @staticmethod
    def from_dict(obj: Any) -> "ContactAddress":
        """Load ContactAddress from dict"""
        _address1 = str(obj.get("address1"))
        _address2 = str(obj.get("address2"))
        _city = str(obj.get("city"))
        _state = str(obj.get("state"))
        _zip = str(obj.get("zip"))
        _country = str(obj.get("country"))
        _country_code = str(obj.get("countryCode"))
        _state_code = str(obj.get("stateCode"))
        return ContactAddress(
            _address1,
            _address2,
            _city,
            _state,
            _zip,
            _country,
            _country_code,
            _state_code,
        )


@dataclass
class ContactEmail:
    """Contact email from dict"""

    address: str
    use_type: str

    @staticmethod
    def from_dict(obj: Any) -> "ContactEmail":
        """Contact email from dict"""
        if isinstance(obj, List):
            _address = str(obj.get("address"))
            _use_type = str(obj.get("useType"))
            return ContactEmail(_address, _use_type)


@dataclass
class ContactPhone:
    """Contact phone"""

    number: str
    use_type: str

    @staticmethod
    def from_dict(obj: Any) -> "ContactPhone":
        """Contact phone from dict"""
        # if isinstance(obj, dict):
        _number = str(obj.get("number"))
        _use_type = str(obj.get("useType"))
        return ContactPhone(_number, _use_type)


@dataclass
class Emails:
    """Email class from LS"""

    contact_email: List[ContactEmail]

    @staticmethod
    def from_dict(obj: Any) -> "Emails":
        """Emails from dict"""
        if obj:
            _contact_email = [ContactEmail.from_dict(y) for y in obj.get("ContactEmail")]
            return Emails(_contact_email)


@dataclass
class Phones:
    """Phones"""

    contact_phone: List[ContactPhone]

    @staticmethod
    def from_dict(obj: Any) -> "Phones":
        """Phones from dict"""
        if obj:
            if isinstance(obj.get("ContactPhone"), List):
                _contact_phone = [ContactPhone.from_dict(y) for y in obj.get("ContactPhone")]
            else:
                _contact_phone = [ContactPhone.from_dict(obj.get("ContactPhone"))]
            return Phones(_contact_phone)
        return Phones("")


@dataclass
class Addresses:
    """Address class from LS"""

    contact_address: ContactAddress

    @staticmethod
    def from_dict(obj: Any) -> "Addresses":
        """Addresses from dict"""
        _contact_address = ContactAddress.from_dict(obj.get("ContactAddress"))
        return Addresses(_contact_address)


@dataclass
class Contact:
    """Contact class from LS"""

    contact_id: str
    custom: str
    no_email: str
    no_phone: str
    no_mail: str
    addresses: Addresses
    phones: Phones
    emails: Emails
    websites: str
    time_stamp: str

    @staticmethod
    def from_dict(obj: Any) -> "Contact":
        """Contact from LS"""
        _contact_id = str(obj.get("contactID"))
        _custom = str(obj.get("custom"))
        _no_email = str(obj.get("noEmail"))
        _no_phone = str(obj.get("noPhone"))
        _no_mail = str(obj.get("noMail"))
        _addresses = Addresses.from_dict(obj.get("Addresses"))
        _phones = Phones.from_dict(obj.get("Phones"))
        _emails = Emails.from_dict(obj.get("Emails"))
        _websites = str(obj.get("Websites"))
        _time_stamp = str(obj.get("timeStamp"))
        return Contact(
            _contact_id,
            _custom,
            _no_email,
            _no_phone,
            _no_mail,
            _addresses,
            _phones,
            _emails,
            _websites,
            _time_stamp,
        )


@dataclass
class Customer:
    """Customer object from LS"""

    customer_id: str
    first_name: str
    last_name: str
    title: str
    company: str
    create_time: str
    time_stamp: str
    archived: str
    contact_id: str
    credit_account_id: str
    customer_type_id: str

    discount_id: str
    tax_category_id: str
    contact: Contact
    is_modified: bool

    def update_phones(self, caller):
        """call API put to update pricing"""
        # TODO use generated payload instead of manual
        if self.contact.phones:
            home_number = ""
            work_number = ""
            mobile_number = ""
            fax_number = ""
            pager_number = ""

            for number in self.contact.phones.contact_phone:
                if number.use_type == "Home":
                    home_number = number.number
                elif number.use_type == "Work":
                    work_number = number.number
                elif number.use_type == "Mobile":
                    mobile_number = number.number
                elif number.use_type == "Fax":
                    fax_number = number.number
                elif number.use_type == "Pager":
                    pager_number = number.number
            put_customer = {
                "Contact": {
                    "Phones": {
                        "ContactPhone": [
                            {"number": f"{mobile_number}", "useType": "Mobile"},
                            {"number": f"{fax_number}", "useType": "Fax"},
                            {"number": f"{pager_number}", "useType": "Pager"},
                            {"number": f"{work_number}", "useType": "Work"},
                            {"number": f"{home_number}", "useType": "Home"},
                        ]
                    }
                }
            }
            put_data(config.LS_URLS["customerPut"].format(customerID=self.customer_id), put_customer, caller)

    @staticmethod
    def from_dict(obj: Any) -> "Customer":
        """Customer object from dict"""
        _customer_id = str(obj.get("customerID"))
        _first_name = str(obj.get("firstName"))
        _last_name = str(obj.get("lastName"))
        _title = str(obj.get("title"))
        _company = str(obj.get("company"))
        _create_time = str(obj.get("createTime"))
        _time_stamp = str(obj.get("timeStamp"))
        _archived = str(obj.get("archived"))
        _contact_id = str(obj.get("contactID"))
        _credit_account_id = str(obj.get("creditAccountID"))
        _customer_type_id = str(obj.get("customerTypeID"))
        _discount_id = str(obj.get("discountID"))
        _tax_category_id = str(obj.get("taxCategoryID"))
        _contact = Contact.from_dict(obj.get("Contact"))
        _is_modified = False
        return Customer(
            _customer_id,
            _first_name,
            _last_name,
            _title,
            _company,
            _create_time,
            _time_stamp,
            _archived,
            _contact_id,
            _credit_account_id,
            _customer_type_id,
            _discount_id,
            _tax_category_id,
            _contact,
            _is_modified,
        )

    @staticmethod
    def get_customers(caller: Button) -> "List[Customer]":
        """API call to get all items.  Walk through categories and pages.
        Convert from json dict to Item object and add to itemList list."""
        # Run API auth
        generate_ls_access()
        customer_list: List[Customer] = []
        current_url = config.LS_URLS["customer"]
        pages = 0
        while current_url:
            response = get_data(current_url, {"load_relations": '["Contact"]', "limit": 100}, caller=caller)
            for customer in response.json().get("Customer"):
                customer_list.append(Customer.from_dict(customer))
            current_url = response.json()["@attributes"]["next"]
            # debug to limit time
            pages += 1
            output = f"Loading page: {pages}"
            caller.text = f"{caller.text.split(chr(10))[0]}\n{output}"
            print(f"{output: <100}", end="\r")
        print()
        return customer_list

    @staticmethod
    def get_customer(customer_id):
        """Get single customer from LS API into Customer object"""
        generate_ls_access()
        response = get_data(config.LS_URLS["customerPut"].format(customerID=customer_id), {"load_relations": '["Contact"]'})

        return Customer.from_dict(response.json().get("Customer"))
