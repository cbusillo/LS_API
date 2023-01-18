import threading
import tkinter as tk
import customtkinter as ctk  # <- import the CustomTkinter module
import updateItemPrice
import updateCustomerPhone

root_tk = tk.Tk()  # create the Tk window like you normally do
root_tk.geometry("600x400")
root_tk.title("Shiny Computers")

def updateCustomerPhoneButtonfn():
    updateCustomerPhone.runUpdateCustomerPhone(label1)
    
def updateItemPriceButtonfn():
    updateItemPrice.runUpdateItemPrice()

def updateItemPriceTableButtonfn():
    pass

label1 = tk.StringVar()
label1.set("test")

# Use CTkButton instead of tkinter Button
updateCustomerPhoneButton = ctk.CTkButton(master=root_tk, corner_radius=10, text="Format Customer Phone Numbers", command=threading.Thread(target=updateCustomerPhoneButtonfn).start)
updateCustomerPhoneButton.pack(pady=20)

updateItemPriceButton = ctk.CTkButton(master=root_tk, corner_radius=10, text="Update iPhone/iPad Prices from Apple and Table", command=updateItemPriceButtonfn)
updateItemPriceButton.pack(pady=20)

updateItemPriceTableButton = ctk.CTkButton(master=root_tk, corner_radius=10, text="Edit Price Table", command=updateItemPriceTableButtonfn)
updateItemPriceTableButton.pack(pady=20)

line1Label = ctk.CTkLabel(master=root_tk, textvariable=label1)
line1Label.pack(pady=20)
label1.set("test2")



root_tk.mainloop()

