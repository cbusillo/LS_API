"""Connect to sickw API"""
import os
from kivy.uix.button import Button
from shiny_api.classes import ipsw_me_ipsw


print(f"Importing {os.path.basename(__file__)}...")


def download_ipsw(caller: Button):
    """Call get_devices"""

    ipsw_me_ipsw.Devices.get_devices(caller)
    caller.disabled = False
    caller.text = caller.text.split("\n")[0]
