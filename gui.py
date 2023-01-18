import tkinter as tk
import customtkinter as ctk  # <- import the CustomTkinter module
import updateItemPrice
import updateCustomerPhone

root_tk = tk.Tk()  # create the Tk window like you normally do
root_tk.geometry("600x400")
root_tk.title("Shiny Computers")

def updateCustomerPhoneButtonfn():
    updateCustomerPhone.runUpdateCustomerPhone()
    
def updateItemPriceButtonfn():
    updateItemPrice.runUpdateItemPrice()

def updateItemPriceTableButtonfn():
    pass

label1 = tk.StringVar()
label1.set("test")

# Use CTkButton instead of tkinter Button
updateCustomerPhoneButton = ctk.CTkButton(master=root_tk, corner_radius=10, text="Format Customer Phone Numbers", command=updateCustomerPhoneButtonfn)
updateCustomerPhoneButton.place(x=25, rely=0.1, anchor=tk.W)

updateItemPriceButton = ctk.CTkButton(master=root_tk, corner_radius=10, text="Update iPhone/iPad Prices from Apple and Table", command=updateItemPriceButtonfn)
updateItemPriceButton.place(x=25, rely=0.25, anchor=tk.W)

updateItemPriceTableButton = ctk.CTkButton(master=root_tk, corner_radius=10, text="Edit Price Table", command=updateItemPriceTableButtonfn)
updateItemPriceTableButton.place(x=400, rely=0.25, anchor=tk.W)

line1Label = ctk.CTkLabel(master=root_tk, textvariable=label1)
line1Label.place(x=25, y=400, anchor=tk.CENTER)
line1Label.pack()
label1.set("test2")



root_tk.mainloop()

