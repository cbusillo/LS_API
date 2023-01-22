"""Connect to sickw API"""
import os
import tkinter as tk
from classes import ipsw_me_ipsw


print(f"Importing {os.path.basename(__file__)}...")


def download_ipsw(label: tk.StringVar):
    """Call get_devices"""
    ipsws = ipsw_me_ipsw.Devices.get_devices(label)
