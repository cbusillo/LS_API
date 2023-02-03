"""Connect to sickw and return a SickwResults object with data from serial_number and service """
import os
import json
from bs4 import BeautifulSoup
import requests
from modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")

APPLE_SERIAL_INFO = 26


class SickwResults:
    """Object built from sickw API results"""

    result_id: int
    status: str
    serial_number: str
    description: str
    name: str
    a_number: str
    model_id: str
    capacity: str
    color: str
    type: str
    year: int

    def __init__(self, serial_number, service) -> None:
        sickw_return = json.loads(self.get_json(serial_number, service))
        if sickw_return["status"].lower() == "success":
            sickw_return_dict = self.html_to_dict(sickw_return["result"])
            if len(sickw_return_dict) > 0:
                self.result_id = sickw_return["id"]
                self.status = sickw_return["status"]
                self.serial_number = sickw_return["imei"]
                self.description = sickw_return_dict["Model Desc"]
                self.name = sickw_return_dict["Model Name"]
                self.a_number = sickw_return_dict["Model Number"]
                self.model_id = sickw_return_dict["Model iD"]
                self.capacity = sickw_return_dict["Capacity"]
                self.color = sickw_return_dict["Color"]
                self.type = sickw_return_dict["Type"]
                self.year = sickw_return_dict["Year"]
        if not self.serial_number:
            self.status = "failed"

    def get_json(self, serial_number, service):
        """Get requested data from Sickw API"""
        current_params = {"imei": serial_number, "service": service, "key": config.SICKW_API_KEY, "format": "JSON"}
        headers = {"User-Agent": "My User Agent 1.0"}
        response = requests.get("https://sickw.com/api.php", params=current_params, headers=headers, timeout=60)
        # response_text = BeautifulSoup(response.text).get_text()
        return response.text

    def html_to_dict(self, html):
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
