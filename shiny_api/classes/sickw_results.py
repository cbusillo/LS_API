"""Connect to sickw and return a SickwResults object with data from serial_number and service """
import os
import json
from typing import List
from bs4 import BeautifulSoup
import requests
from shiny_api.modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")

# Constants for sickw service codes
APPLE_SERIAL_INFO = 26


class SickwResults:
    """Object built from sickw API results"""

    result_id: int = 0
    status: str
    serial_number: str
    description: str = ""
    name: str = ""
    a_number: str = ""
    model_id: str = ""
    capacity: str = ""
    color: str = ""
    type: str = ""
    year: int = 0

    def __init__(self, serial_number: str, service: int) -> None:
        """Instantiate result with data from API from passed serial number and service.  Set status to false if sickw
        says not success or no HTML result string"""
        self.serial_number = serial_number
        sickw_return = json.loads(self.get_json(serial_number, service))
        if sickw_return.get("status").lower() == "success":
            sickw_return_dict = self.html_to_dict(sickw_return.get("result"))
            if sickw_return_dict:
                self.result_id = sickw_return.get("id")
                self.status = sickw_return.get("status")
                self.description = sickw_return_dict.get("Model Desc")
                self.name = sickw_return_dict.get("Model Name")
                self.a_number = sickw_return_dict.get("Model Number")
                self.model_id = sickw_return_dict.get("Model iD")
                self.capacity = sickw_return_dict.get("Capacity")
                self.color = sickw_return_dict.get("Color")
                self.type = sickw_return_dict.get("Type")
                self.year = sickw_return_dict.get("Year")
                return
        self.status = "failed"

    def get_json(self, serial_number: str, service: int):
        """Get requested data from Sickw API"""
        current_params = {"imei": serial_number, "service": service, "key": config.SICKW_API_KEY, "format": "JSON"}
        headers = {"User-Agent": "My User Agent 1.0"}
        response = requests.get("https://sickw.com/api.php", params=current_params, headers=headers, timeout=60)
        # response_text = BeautifulSoup(response.text).get_text()
        return response.text

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
