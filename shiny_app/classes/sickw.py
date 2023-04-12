"""Connect to sickw and return a SickwResults object with data from serial_number and service """
from dataclasses import dataclass
from pathlib import Path
from bs4 import BeautifulSoup
import requests
from shiny_app.modules.load_config import Config


class SickConstants:
    """Constants for sickw service codes"""

    APPLE_SERIAL_INFO = 26
    APPLE_FINDMY = 3


@dataclass
class Sickw:
    """Object built from sickw API results"""

    status: str = "failed"

    def __init__(self, imei: str = "", service: int = SickConstants.APPLE_SERIAL_INFO):
        """Instantiate result with data from API from
        passed serial number and service.  Set status to false if sickw
        says not success or no HTML result string"""

        current_params = {"imei": imei, "service": service, "key": Config.SICKW_API_KEY, "format": "JSON"}
        headers = {"User-Agent": "My User Agent 1.0"}
        response = requests.get("https://sickw.com/api.php", params=current_params, headers=headers, timeout=60)
        response_json = response.json()

        self.serial_number = imei
        self.status = response_json.get("status").lower()
        if self.status != "success":
            self.status = "failed"
            return
        result_data = response_json.get("result")
        sickw_return_dict = self.html_to_dict(result_data)

        if "Find My iPhone:" in result_data:
            if "<b>OFF</b>" in result_data:
                self.findmy = False
            elif "<b>ON</b>" in result_data:
                self.findmy = True

        if not sickw_return_dict:
            return
        self.result_id: int = int(response_json.get("id"))
        self.status: str = response_json.get("status")
        self.description: str = sickw_return_dict.get("Model Desc", "")
        self.name: str = sickw_return_dict.get("Model Name", "")
        self.a_number: str = sickw_return_dict.get("Model Number", "")
        self.model_id: str = sickw_return_dict.get("Model iD", "")
        self.capacity: str = sickw_return_dict.get("Capacity", "")
        self.color: str = sickw_return_dict.get("Color", "")
        self.type: str = sickw_return_dict.get("Type", "")
        self.year: int = int(sickw_return_dict.get("Year", ""))

    def __str__(self) -> str:
        if self.status == "failed":
            return "No results"

        print_string = (
            f"{self.name} {self.description} {self.color} {self.capacity}\n"
            + f"{self.model_id} {self.a_number} {self.type} {self.year}\n"
            + f"{self.status} Findmy: {self.findmy_formatted}\n"
        )
        return print_string

    @property
    def findmy_formatted(self) -> str:
        """load file of serials and write results to file"""
        formatted_result = None

        if self.status == "failed" or self.findmy is None:
            formatted_result = "FAILED"
        elif self.findmy is False:
            formatted_result = "Off"
        elif self.findmy is True:
            formatted_result = "On"

        return f"{formatted_result}\n"

    @staticmethod
    def html_to_dict(html: str) -> dict[str, str]:
        """generate dict from html returned in result"""
        soup = BeautifulSoup(html, "html.parser")
        return_dict = {}
        for line in soup.findAll("br"):
            br_next = line.nextSibling
            if br_next != line and br_next is not None:
                data = br_next.split(":")
                return_dict[data[0]] = data[1].strip()
        return return_dict

    @staticmethod
    def success_count(results: "list[Sickw]") -> int:
        """Return count of total sucessful Sickw results"""
        return_count = 0
        for result in results:
            if result.name:
                return_count += 1

        return return_count

    @staticmethod
    def search_list_for_serial(results: "list[Sickw]", serial: str) -> tuple[str, str] | None:
        """Return the device description from provided serial number and list of results"""
        for result in results:
            if result.serial_number == serial:
                return result.name, result.status

        return None

    @staticmethod
    def findmy_from_file(serial_filename: Path, output_filename: Path):
        """load file of serials and write results to file"""
        with open(serial_filename, "r", encoding="utf-8") as serial_file:
            serials = serial_file.readlines()
        with open(output_filename, "w", encoding="utf-8") as output_file:
            for serial in serials:
                sickw_item = Sickw(imei=serial.strip(), service=SickConstants.APPLE_FINDMY)
                output_text = f"Serial Number: {sickw_item.serial_number} Findmy: {sickw_item.findmy_formatted}"
                output_file.write(output_text)
                print(output_text, end="")


if __name__ == "__main__":
    Sickw.findmy_from_file(Path("temp/serials.txt"), Path("temp/results.txt"))
