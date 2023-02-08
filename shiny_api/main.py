#!/usr/bin/env python3.11
"""Main GUI File"""
import datetime
import platform
import logging
import sys
from functools import partial
from threading import Thread
from typing import List
import subprocess
from kivy.app import App
from kivy.config import Config
from kivy.logger import Logger, LOG_LEVELS
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from shiny_api.modules import weblistener
from shiny_api.modules import update_customer_phone
from shiny_api.modules import get_ipsws
from shiny_api.modules import load_config as config
from shiny_api.modules import update_item_price
from shiny_api.modules import label_print

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

LABELS = [
    "Good",
    "Bad",
    "SSD Fan Control",
    "RMA",
    "MS RMA",
    "IG RMA",
    "PT RMA",
    "Grade C",
    "Grade D",
    "Grade F",
    "Part out",
    "Bench Use",
    "app.shinycomputers.com",
    "TBT",
    "Donated",
    "Customer",
    "Fully Functional",
]


class MainScreen(Screen):
    """Define main screen grid layout"""

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        self.grid_layout = GridLayout()
        self.grid_layout.cols = 1
        self.grid_layout.padding = 100
        update_customer_phone_button = Button(text="Format Customer Phone Numbers")
        update_customer_phone_button.bind(on_press=self.update_customer_phone)
        self.grid_layout.add_widget(update_customer_phone_button)

        update_item_price_button = Button(text="Update iPhone/iPad Prices from Apple and Table")
        update_item_price_button.bind(on_press=self.update_item_price)
        self.grid_layout.add_widget(update_item_price_button)

        open_serial_scanner_button = Button(text="Load Serial Number Scanner")
        open_serial_scanner_button.bind(on_press=self.open_serial_scanner)
        self.grid_layout.add_widget(open_serial_scanner_button)

        open_ipsw_downloader_button = Button(text="Load IPSW downloader")
        open_ipsw_downloader_button.bind(on_press=self.open_ipsw_downloader)
        self.grid_layout.add_widget(open_ipsw_downloader_button)

        slide_label_printer_button = Button(text="Open Label Printer")
        slide_label_printer_button.bind(on_press=self.changer)
        self.grid_layout.add_widget(slide_label_printer_button)

        start_api_server_button = Button(text="Start API Server")
        start_api_server_button.bind(on_press=self.start_api_server)
        self.grid_layout.add_widget(start_api_server_button)
        self.add_widget(self.grid_layout)

    def changer(self, *_):
        """Slide to malabel_printer_screen"""
        self.manager.current = "label_printer_screen"

    def update_item_price(self, caller: Button):
        """Run the Item Pricing Function"""
        thread = Thread(target=update_item_price.run_update_item_price, args=[caller])
        thread.daemon = True
        caller.text += "\nrunning..."
        caller.disabled = True
        thread.start()

    def update_customer_phone(self, caller: Button):
        """Run the Customer Phone Number Formatting Function"""
        thread = Thread(target=update_customer_phone.run_update_customer_phone, args=[caller])
        thread.daemon = True
        caller.text += "\nrunning..."
        caller.disabled = True
        thread.start()

    def open_ipsw_downloader(self, caller: Button):
        """Run the IPSW downloader"""
        thread = Thread(target=get_ipsws.download_ipsw, args=[caller])
        thread.daemon = True
        caller.text += "\nrunning..."
        caller.disabled = True
        thread.start()

    def open_serial_scanner(self, _):
        """Open the serial number scanner"""
        subprocess.Popen(f"{sys.executable} -m shiny_api.serial_camera", shell=True)

    def start_api_server(self, caller: Button):
        """Start API Server for LS"""
        thread = Thread(target=weblistener.start_weblistener, args=[caller])
        thread.daemon = True
        caller.text += "\nrunning..."
        caller.disabled = True
        thread.start()


class LabelPrinterScreen(Screen):
    """Define main screen grid layout"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_grid = GridLayout()
        main_grid.cols = 1
        main_grid.padding = 100

        label_grid = GridLayout()
        label_grid.cols = 3
        label_grid.padding = 100

        label_buttons: List[Button] = []

        for index, label in enumerate(LABELS):
            label_buttons.append(Button(text=label))
            label_buttons[index].bind(on_press=partial(self.print_labels, text=label))
            label_grid.add_widget(label_buttons[index])

        main_grid.add_widget(label_grid)

        main_grid.slide_label_printer_button = Button(text="Back to main screen", size_hint=(1, 0.1))
        main_grid.slide_label_printer_button.bind(on_press=self.changer)
        main_grid.add_widget(main_grid.slide_label_printer_button)

        self.add_widget(main_grid)

    def changer(self, *_):
        """Slide to main_screen"""
        self.manager.current = "main_screen"

    def print_labels(self, _, text):
        """Print label from input text with date"""
        today = datetime.date.today()
        Thread(
            target=partial(
                label_print.print_text,
                f"{text}\\&{today.month}.{today.day}.{today.year}",
            )
        ).start()


class APIApp(App):
    """Initialize app settings"""

    def build(self):
        screen_manager = ScreenManager()
        main_screen = MainScreen(name="main_screen")
        label_printer_screen = LabelPrinterScreen(name="label_printer_screen")
        screen_manager.add_widget(main_screen)
        screen_manager.add_widget(label_printer_screen)
        return screen_manager


def start_gui():
    """start the gui, call from project or if run directly"""
    interface = APIApp()
    interface.run()


if __name__ == "__main__":
    start_gui()
