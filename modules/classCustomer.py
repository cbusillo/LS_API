import os
import json
from typing import List, Any
from dataclasses import dataclass
import tkinter as tk

from modules.connect import urls, accessHeader, generate_access, get_data, put_data

print("Importing {}...".format(os.path.basename(__file__)))

def toJSON(tojson):
    return json.dumps(tojson, default=lambda o: o.__dict__, sort_keys=True, indent=None, separators=(', ', ': '))

@dataclass
class ContactAddress:
    address1: str
    address2: str
    city: str
    state: str
    zip: str
    country: str
    countryCode: str
    stateCode: str

    @staticmethod
    def from_dict(obj: Any) -> 'ContactAddress':
        _address1 = str(obj.get("address1"))
        _address2 = str(obj.get("address2"))
        _city = str(obj.get("city"))
        _state = str(obj.get("state"))
        _zip = str(obj.get("zip"))
        _country = str(obj.get("country"))
        _countryCode = str(obj.get("countryCode"))
        _stateCode = str(obj.get("stateCode"))
        return ContactAddress(_address1, _address2, _city, _state, _zip, _country, _countryCode, _stateCode)

@dataclass
class ContactEmail:
    address: str
    useType: str

    @staticmethod
    def from_dict(obj: Any) -> 'ContactEmail':
        if isinstance(obj, List):
            _address = str(obj.get("address"))
            _useType = str(obj.get("useType"))
            return ContactEmail(_address, _useType)

@dataclass
class ContactPhone:
    number: str
    useType: str

    @staticmethod
    def from_dict(obj: Any) -> 'ContactPhone':
        #if isinstance(obj, dict):
        _number = str(obj.get("number"))
        _useType = str(obj.get("useType"))
        return ContactPhone(_number, _useType)

@dataclass
class Emails:
    ContactEmail: List[ContactEmail]

    @staticmethod
    def from_dict(obj: Any) -> 'Emails':
        if obj:
            _ContactEmail = [ContactEmail.from_dict(y) for y in obj.get("ContactEmail")]
            return Emails(_ContactEmail)

@dataclass
class Phones:
    ContactPhone: List[ContactPhone]

    @staticmethod
    def from_dict(obj: Any) -> 'Phones':
        if obj:
            if isinstance(obj.get("ContactPhone"), List):
                _ContactPhone = [ContactPhone.from_dict(y) for y in obj.get("ContactPhone")]
            else:
                _ContactPhone = [ContactPhone.from_dict(obj.get("ContactPhone"))]
            return Phones(_ContactPhone)

@dataclass
class Addresses:
    ContactAddress: ContactAddress

    @staticmethod
    def from_dict(obj: Any) -> 'Addresses':
        _ContactAddress = ContactAddress.from_dict(obj.get("ContactAddress"))
        return Addresses(_ContactAddress)

@dataclass
class Contact:
    contactID: str
    custom: str
    noEmail: str
    noPhone: str
    noMail: str
    Addresses: Addresses
    Phones: Phones
    Emails: Emails
    Websites: str
    timeStamp: str

    @staticmethod
    def from_dict(obj: Any) -> 'Contact':
        _contactID = str(obj.get("contactID"))
        _custom = str(obj.get("custom"))
        _noEmail = str(obj.get("noEmail"))
        _noPhone = str(obj.get("noPhone"))
        _noMail = str(obj.get("noMail"))
        _Addresses = Addresses.from_dict(obj.get("Addresses"))
        _Phones = Phones.from_dict(obj.get("Phones"))
        _Emails = Emails.from_dict(obj.get("Emails"))
        _Websites = str(obj.get("Websites"))
        _timeStamp = str(obj.get("timeStamp"))
        return Contact(_contactID, _custom, _noEmail, _noPhone, _noMail, _Addresses, _Phones, _Emails, _Websites, _timeStamp)



@dataclass
class Customer:
    customerID: str
    firstName: str
    lastName: str
    title: str
    company: str
    createTime: str
    timeStamp: str
    archived: str
    contactID: str
    creditAccountID: str
    customerTypeID: str
    discountID: str
    taxCategoryID: str
    Contact: Contact
    isModified: bool
    
    def update_phones(self):
        #call API put to update pricing
        #TODO use generated payload instead of manual "757-535-1545"
        if (self.Contact.Phones):
            homeNumber = ''
            workNumber = ''
            mobileNumber = ''
            faxNumber = ''
            pagerNumber = ''
            if self.firstName.lower() == 'chuck':
                pass
            for number in self.Contact.Phones.ContactPhone:
                if(number.useType == 'Home'):
                    homeNumber = number.number
                elif (number.useType == 'Work'):
                    workNumber = number.number
                elif (number.useType == 'Mobile'):
                    mobileNumber = number.number
                elif (number.useType == 'Fax'):
                    faxNumber = number.number
                elif (number.useType == 'Pager'):
                    pagerNumber = number.number
            putCustomer = {"Contact": {"Phones": {"ContactPhone": [
                {"number": "{}".format(mobileNumber), "useType": "Mobile"},
                {"number": "{}".format(faxNumber), "useType": "Fax"},
                {"number": "{}".format(pagerNumber), "useType": "Pager"},
                {"number": "{}".format(workNumber),"useType": "Work"},
                {"number": "{}".format(homeNumber),"useType": "Home"}]}}}
            put_data(urls["customerPut"].format(customerID = self.customerID), putCustomer)

    @staticmethod
    def from_dict(obj: Any) -> 'Customer':
        _customerID = str(obj.get("customerID"))
        _firstName = str(obj.get("firstName"))
        _lastName = str(obj.get("lastName"))
        _title = str(obj.get("title"))
        _company = str(obj.get("company"))
        _createTime = str(obj.get("createTime"))
        _timeStamp = str(obj.get("timeStamp"))
        _archived = str(obj.get("archived"))
        _contactID = str(obj.get("contactID"))
        _creditAccountID = str(obj.get("creditAccountID"))
        _customerTypeID = str(obj.get("customerTypeID"))
        _discountID = str(obj.get("discountID"))
        _taxCategoryID = str(obj.get("taxCategoryID"))
        _Contact = Contact.from_dict(obj.get("Contact"))
        _isModified = False
        return Customer(_customerID, _firstName, _lastName, _title, _company, _createTime, _timeStamp, _archived, _contactID, _creditAccountID, _customerTypeID, _discountID, _taxCategoryID, _Contact, _isModified)

    #passing label 
    @staticmethod
    def get_customers(label: tk.StringVar) -> 'List[Customer]':
        #Run API auth
        generate_access()
        #API call to get all items.  Walk through categories and pages.  Convert from json dict to Item object and add to itemList list.
        customerList: List[Customer] = []
        currentURL = urls["customer"]
        pages = 0
        while currentURL:
            response =  get_data(currentURL,{'load_relations':'["Contact"]', 'limit': 100})
            for customer in response.json().get("Customer"):
                customerList.append(Customer.from_dict(customer))
            currentURL = response.json()["@attributes"]["next"]
            #debug to limit time
            pages += 1
            label.set(f"Loading page: {pages}")
            print(f"Loading page: {pages}                                                  ", end='\r')
        print()
        return customerList