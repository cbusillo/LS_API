"""Connect to sickw API"""
import os
import tkinter as tk
from classes import ipsw_class


print(f"Importing {os.path.basename(__file__)}...")


def download_ipsw(label: tk.StringVar):
    """Call get_devices"""
    ipsws = ipsw_class.Devices.get_devices(label)
