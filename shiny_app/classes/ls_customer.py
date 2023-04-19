"""Class to import customer objects from LS API"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Self, TYPE_CHECKING

from shiny_app.classes.ls_client import BaseLSEntity

if TYPE_CHECKING:
    from shiny_app.django_server.customers.models import Customer as ShinyCustomer


@dataclass
class Customer(BaseLSEntity):
    """Customer object from LS"""

    class_params = {"load_relations": '["Contact"]'}

    @dataclass
    class Phone(BaseLSEntity):
        """Phone"""

        number: str
        number_type: str

        @classmethod
        def from_json(cls, data_json: dict[str, Any]) -> Self:
            """Phone object from dict"""
            return cls(number=data_json.get("number", ""), number_type=data_json.get("useType", ""))

    @dataclass
    class Email(BaseLSEntity):
        """Email"""

        address: str
        address_type: str

        @classmethod
        def from_json(cls, data_json: dict[str, Any]) -> Self:
            """Email object from dict"""
            return cls(address=data_json.get("address", ""), address_type=data_json.get("useType", ""))

    customer_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    create_time: Optional[datetime] = None
    time_stamp: Optional[datetime] = None
    archived: Optional[bool] = None
    contact_id: Optional[int] = None
    credit_account_id: Optional[int] = None
    customer_type_id: Optional[int] = None
    tax_category_id: Optional[int] = None
    phones: list[Phone] = field(default_factory=lambda: [])
    emails: list[Email] = field(default_factory=lambda: [])

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)

        if self.customer_id and self.fetch_from_api:
            customer_json = next(self.get_entities_json(entity_id=self.customer_id))
            customer = self.from_json(customer_json)
            self.__dict__.update(customer.__dict__)

        # only used for saving phone numbers back to lightspeed
        if isinstance(self.phones, list) and all(isinstance(item, dict) for item in self.phones):
            phones_json = self.phones.copy()
            self.phones.clear()
            for phone in phones_json:
                if isinstance(phone, dict) and all(isinstance(key, str) for key in phone):
                    self.phones.append(self.Phone.discard_extra_args(**phone))

    @classmethod
    def from_json(cls, data_json: dict[str, Any]) -> Self:
        """Customer object from dict"""
        if not isinstance(data_json, dict):
            raise ValueError("Customer must be a dict: " + str(data_json))

        contact_phones_list_json = data_json.get("Contact", {}).get("Phones", {})
        contact_phones_json = []
        if isinstance(contact_phones_list_json, dict):
            contact_phones_json = contact_phones_list_json.get("ContactPhone", [])
        if not isinstance(contact_phones_json, list):
            contact_phones_json = [contact_phones_json]

        phones_json = [cls.Phone(phone.get("number"), phone.get("useType")) for phone in contact_phones_json]

        contact_emails_list_json = data_json.get("Contact", {}).get("Emails", {})
        contact_email_json = []
        if isinstance(contact_emails_list_json, dict):
            contact_email_json = contact_emails_list_json.get("ContactEmail", [])
        if not isinstance(contact_email_json, list):
            contact_email_json = [contact_email_json]

        emails_json = [cls.Email(email.get("address"), email.get("useType")) for email in contact_email_json]

        customer_json_transformed = {
            "customer_id": cls.safe_int(data_json.get("customerID")),
            "first_name": data_json.get("firstName", "").strip(),
            "last_name": data_json.get("lastName", "").strip(),
            "company": data_json.get("company", "").strip(),
            "title": data_json.get("title", "").strip(),
            "create_time": cls.string_to_datetime(data_json.get("createTime")),
            "time_stamp": cls.string_to_datetime(data_json.get("timeStamp")),
            "archived": data_json.get("archived", "false").lower() == "true",
            "contact_id": cls.safe_int(data_json.get("contactID")),
            "credit_account_id": cls.safe_int(data_json.get("creditAccountID")),
            "customer_type_id": cls.safe_int(data_json.get("customerTypeID")),
            "tax_category_id": cls.safe_int(data_json.get("taxCategoryID")),
            "phones": phones_json,
            "emails": emails_json,
        }
        return cls(**customer_json_transformed)

    def create(self) -> int:
        """Create LS customer and return customer_id"""
        mobile_number = ""
        email_address = ""
        for phone in self.phones:
            if phone.number_type == "Mobile":
                mobile_number = phone.number
                break
        if isinstance(self.emails, list) and isinstance(self.emails[0], dict):
            email_address = self.emails[0].get("address")
        post_customer = {
            "firstName": self.first_name,
            "lastName": self.last_name,
            "Contact": {
                "Emails": {"ContactEmail": [{"address": email_address, "useType": "Primary"}]},
                "Phones": {"ContactPhone": [{"number": mobile_number, "useType": "Mobile"}]},
            },
        }

        return self.post_entity_json(post_customer)

    def update_phones(self) -> None:
        """call API put to update pricing"""
        if self.phones is None or self.customer_id is None:
            raise ValueError("Customer must have phones and customer_id to update")

        numbers = {}
        for phone in self.phones:
            numbers[phone.number_type] = phone.number

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
        self.put_entity_json(self.customer_id, put_customer)

    def shiny_customer_from_ls(self, shiny_customer: "ShinyCustomer", start_time: datetime):
        """translation layer for LSCustomer to ShinyCustomer"""
        # pylint: disable=import-outside-toplevel
        from shiny_app.django_server.customers.models import (
            Phone as ShinyPhone,
            Email as ShinyEmail,
        )

        shiny_customer.ls_customer_id = self.customer_id
        shiny_customer.first_name = self.first_name
        shiny_customer.last_name = self.last_name
        shiny_customer.title = self.title
        shiny_customer.company = self.company
        shiny_customer.create_time = self.time_stamp or start_time
        shiny_customer.update_time = start_time
        shiny_customer.update_from_ls_time = start_time
        shiny_customer.archived = self.archived
        shiny_customer.contact_id = self.contact_id
        shiny_customer.credit_account_id = self.credit_account_id
        shiny_customer.customer_type_id = self.customer_type_id
        shiny_customer.tax_category_id = self.tax_category_id
        functions_to_execute_after = []

        for phone in self.phones:
            if not ShinyPhone.objects.filter(number=phone.number, number_type=phone.number_type, customer=shiny_customer).exists():
                functions_to_execute_after.append(
                    ShinyPhone(number=phone.number, number_type=phone.number_type, customer=shiny_customer).save
                )

        for email in self.emails:
            if not ShinyEmail.objects.filter(
                address=email.address, address_type=email.address_type, customer=shiny_customer
            ).exists():
                functions_to_execute_after.append(
                    ShinyEmail(address=email.address, address_type=email.address_type, customer=shiny_customer).save
                )

        return shiny_customer, functions_to_execute_after
