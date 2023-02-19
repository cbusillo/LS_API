"""Connect to sickw and return a SickwResults object with data from serial_number and service """
from dataclasses import dataclass
import os
from typing import List
from bs4 import BeautifulSoup
import requests
from shiny_api.modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")

# Constants for sickw service codes
APPLE_SERIAL_INFO = 26


@dataclass
class SickwResults:
    """Object built from sickw API results"""

    status: str = "failed"

    def __init__(self, serial_number: str, service: int = APPLE_SERIAL_INFO) -> None:
        """Instantiate result with data from API from passed serial number and service.  Set status to false if sickw
        says not success or no HTML result string"""

        current_params = {"imei": serial_number, "service": service, "key": config.SICKW_API_KEY, "format": "JSON"}
        headers = {"User-Agent": "My User Agent 1.0"}
        response = requests.get("https://sickw.com/api.php", params=current_params, headers=headers, timeout=60)
        response_json = response.json()

        self.serial_number = serial_number
        if response_json.get("status").lower() != "success":
            return

        sickw_return_dict = self.html_to_dict(response_json.get("result"))
        if not sickw_return_dict:
            return
        self.result_id: int = response_json.get("id")
        self.status: str = response_json.get("status")
        self.description: str = sickw_return_dict.get("Model Desc")
        self.name: str = sickw_return_dict.get("Model Name")
        self.a_number: str = sickw_return_dict.get("Model Number")
        self.model_id: str = sickw_return_dict.get("Model iD")
        self.capacity: str = sickw_return_dict.get("Capacity")
        self.color: str = sickw_return_dict.get("Color")
        self.type: str = sickw_return_dict.get("Type")
        self.year: int = sickw_return_dict.get("Year")
        return

    def __str__(self) -> str:
        if self.status == "failed":
            return "No results"

        print_string = (
            f"{self.name} {self.description} {self.color} {self.capacity}\n"
            + f"{self.model_id} {self.a_number} {self.type} {self.year}\n"
            + f"{self.status}\n"
        )
        return print_string

    def html_to_dict(self, html: str):
        """generate dict from html returned in result"""
        soup = BeautifulSoup(html, "html.parser")
        return_dict = {}
        for line in soup.findAll("br"):
            br_next = line.nextSibling
            if br_next != line and br_next is not None:
                data = br_next.split(":")
                return_dict[data[0]] = data[1].strip()
                # return_list.append(br_next)

        return return_dict

    @staticmethod
    def search_list_for_serial(serial: str, sickw_history: "List[SickwResults]") -> str:
        """Return the device description from provided serial number and list of results"""
        for result in sickw_history:
            if result.serial_number == serial:
                return result.name, result.status

    @staticmethod
    def success_count(sickw_history: "List[SickwResults]") -> int:
        """Return count of total sucessful Sickw results"""
        return_count = 0
        for result in sickw_history:
            if result.name:
                return_count += 1

        return return_count
