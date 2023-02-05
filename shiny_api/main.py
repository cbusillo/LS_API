#!/usr/bin/env python3.11
"""Main GUI File"""
import platform
import logging
import sys
from threading import Thread
import subprocess
from kivy.app import App
from kivy.config import Config
from kivy.logger import Logger, LOG_LEVELS
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from shiny_api.modules import weblistener
from shiny_api.modules import update_customer_phone
from shiny_api.modules import get_ipsws
from shiny_api.modules import load_config as config
from shiny_api.modules import update_item_price

if platform.node() == "Chris-MBP":
    config.DEBUG_CODE = True
    config.DEBUG_LOGGING = False

Config.set("kivy", "log_level", "warning")
Logger.setLevel(LOG_LEVELS["warning"])
logging.getLogger().setLevel(logging.WARNING)
if config.DEBUG_LOGGING:
    logging.getLogger().setLevel(logging.DEBUG)
    Logger.setLevel(LOG_LEVELS["debug"])
    Config.set("kivy", "log_level", "debug")
Config.write()


class MainGrid(GridLayout):
    """Define main screen grid layout"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.padding = 100
        self.update_customer_phone_btn = Button(text="Format Customer Phone Numbers", halign="center")
        self.update_customer_phone_btn.bind(on_press=self.update_customer_phone_fn)
        self.add_widget(self.update_customer_phone_btn)

        self.update_item_price_btn = Button(text="Update iPhone/iPad Prices from Apple and Table", halign="center")
        self.update_item_price_btn.bind(on_press=self.update_item_price_fn)
        self.add_widget(self.update_item_price_btn)

        self.open_serial_scanner_btn = Button(text="Load Serial Number Scanner")
        self.open_serial_scanner_btn.bind(on_press=self.open_serial_scanner_fn)
        self.add_widget(self.open_serial_scanner_btn)

        self.open_ipsw_downloader_btn = Button(text="Load IPSW downloader", halign="center")
        self.open_ipsw_downloader_btn.bind(on_press=self.open_ipsw_downloader_fn)
        self.add_widget(self.open_ipsw_downloader_btn)

        self.start_api_server_btn = Button(text="Start API Server")
        self.start_api_server_btn.bind(on_press=self.start_api_server_fn)
        self.add_widget(self.start_api_server_btn)

    def update_item_price_fn(self, caller: Button):
        """Run the Item Pricing Function"""
        thread = Thread(target=update_item_price.run_update_item_price, args=[caller])
        thread.daemon = True
        caller.text += "\nrunning..."
        caller.disabled = True
        thread.start()

    def update_customer_phone_fn(self, caller: Button):
        """Run the Customer Phone Number Formatting Function"""
        thread = Thread(target=update_customer_phone.run_update_customer_phone, args=[caller])
        thread.daemon = True
        caller.text += "\nrunning..."
        caller.disabled = True
        thread.start()

    def open_ipsw_downloader_fn(self, caller: Button):
        """Run the IPSW downloader"""
        thread = Thread(target=get_ipsws.download_ipsw, args=[caller])
        thread.daemon = True
        caller.text += "\nrunning..."
        caller.disabled = True
        thread.start()

    #     get_ipsws.download_ipsw(label1)

    def open_serial_scanner_fn(self, _):
        """Open the serial number scanner"""
        # caller.text += "\nrunning..."
        subprocess.Popen(f"{sys.executable} -m shiny_api.serial_camera", shell=True)
        # scanner = camera.SerialCamera()
        # popup_window = Popup(title="Serial Scanner", content=scanner, size_hint=(None, None), size=(1024, 768))
        # popup_window.open()

        # camera.take_serial_image(caller)

    def start_api_server_fn(self, caller: Button):
        """Start API Server for LS"""
        thread = Thread(target=weblistener.start_weblistener, args=[caller])
        thread.daemon = True
        caller.text += "\nrunning..."
        caller.disabled = True
        thread.start()


class APIApp(App):
    """Initialize app settings"""

    def build(self):
        # Window.left = 220  # 0
        # Window.top = 100

        return MainGrid()


def start_gui():
    """start the gui, call from project or if run directly"""
    interface = APIApp()
    interface.run()


if __name__ == "__main__":
    start_gui()
