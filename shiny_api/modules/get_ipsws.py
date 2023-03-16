"""Connect to sickw API"""
import os
from shiny_api.classes import ipsw_me_ipsw


print(f"Importing {os.path.basename(__file__)}...")


def download_ipsw():
    """Call get_devices"""
    ipsw_me_ipsw.Device.download_all_firmwares()
