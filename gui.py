#!/usr/bin/env python3.11
"""Main GUI File"""
import platform
import logging
from kivy.logger import Logger, LOG_LEVELS

Logger.setLevel(LOG_LEVELS["warning"])
from threading import Thread
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from modules import weblistener
from modules import update_item_price
from modules import update_customer_phone
from modules import camera
from modules import get_ipsws
from modules import load_config as config

if platform.node() == "Chris-MBP":
    config.DEBUG_CODE = True
    config.DEBUG_LOGGING = False

logging.getLogger().setLevel(logging.WARNING)
if config.DEBUG_LOGGING:
    logging.getLogger().setLevel(logging.DEBUG)
    Logger.setLevel(LOG_LEVELS["debug"])


class MainGrid(GridLayout):
    """Define main screen grid layout"""

    def __init__(self, **kwargs):
        super(MainGrid, self).__init__(**kwargs)
        self.cols = 1
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
        caller.text = caller.text + "\nrunning..."
        caller.disabled = True
        thread.start()

    def update_customer_phone_fn(self, caller: Button):
        """Run the Customer Phone Number Formatting Function"""
        thread = Thread(target=update_customer_phone.run_update_customer_phone, args=[caller])
        thread.daemon = True
        caller.text = caller.text + "\nrunning..."
        caller.disabled = True
        thread.start()

    def open_ipsw_downloader_fn(self, caller: Button):
        """Run the IPSW downloader"""
        thread = Thread(target=get_ipsws.download_ipsw, args=[caller])
        thread.daemon = True
        caller.text = caller.text + "\nrunning..."
        caller.disabled = True
        thread.start()

    #     get_ipsws.download_ipsw(label1)

    def open_serial_scanner_fn(self, caller: Button):
        """Open the serial number scanner"""
        caller.text = caller.text + "\nrunning..."
        camera.take_serial_image(caller)
        # thread = Thread(target=camera.take_serial_image, args=[caller])
        # thread.daemon = True
        # caller.text = caller.text + "\nrunning..."
        # caller.disabled = True
        # thread.start()

    def start_api_server_fn(self, caller: Button):
        """Start API Server for LS"""
        thread = Thread(target=weblistener.start_weblistener, args=[caller])
        thread.daemon = True
        caller.text = caller.text + "\nrunning..."
        caller.disabled = True
        thread.start()


class APIApp(App):
    """Initialize app settings"""

    def build(self):
        Window.left = 2200
        Window.top = 100

        return MainGrid()


interface = APIApp()
interface.run()
