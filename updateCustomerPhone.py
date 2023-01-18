import modules.classCustomer as classCustomer
import re

def runUpdateCustomerPhone():
    customers = classCustomer.Customer.get_customers()
    customersUpdated = 0
    for index, customer in enumerate(customers):
        if customer.Contact.Phones:
            for indexNumber, eachNumber in enumerate(customer.Contact.Phones.ContactPhone):
                if eachNumber.number != re.sub(r'[^0-9x]', '', eachNumber.number):
                    eachNumber.number = re.sub(r'[^0-9x]', '', eachNumber.number)
                    customer.isModified = True
                if len(eachNumber.number) == 7:
                    eachNumber.number = '757' + eachNumber.number 
                    customer.isModified = True
                #print(f'{index} {customer.contactID} {customer.Contact.Phones.ContactPhone[indexNumber].number} {customer.firstName}')
        if customer.isModified == True:
            customersUpdated += 1
            print(f"{customersUpdated}: Updating Customer #{index} out of {len(customers)}                         ", end='\r')
            customer.update_phones()