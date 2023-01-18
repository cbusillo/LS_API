import modules.classCustomer as classCustomer
import re
import tkinter as tk

def runUpdateCustomerPhone(label: tk.StringVar):
    label.set("Running")
    customers = classCustomer.Customer.get_customers(label)
    customersUpdated = 0
    for index, customer in enumerate(customers):
        if customer.Contact.Phones:
            for eachNumber in customer.Contact.Phones.ContactPhone:
                cleanedNumber = re.sub(r'[^0-9x]', '', eachNumber.number)
                if eachNumber.number != cleanedNumber:
                    eachNumber.number = cleanedNumber
                    customer.isModified = True
                if len(eachNumber.number) == 7:
                    eachNumber.number = '757' + eachNumber.number 
                    customer.isModified = True
        if customer.isModified == True:
            customersUpdated += 1
            print(f"{customersUpdated}: Updating Customer #{index} out of {len(customers)}                         ", end='\r')        
            label.set(f"{customersUpdated}: Updating Customer #{index} out of {len(customers)}")
            customer.update_phones()