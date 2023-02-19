"""PhoneCheck class for information from PhoneCheck's API"""
import os
import json
from datetime import datetime
from dataclasses import dataclass
import requests
import shiny_api.modules.load_config as config


print(f"Importing {os.path.basename(__file__)}...")


@dataclass
class Device:
    """Describe object returned from PC_API_URL["device"]"""

    blacklist = ["", "Sim Reader"]
    success: bool = False

    def __init__(self, serial_number: str) -> None:
        """load data from API"""
        params = {"Apikey": config.PHONECHECK_API_KEY, "imei": serial_number, "Username": "cloudshinycomputers"}
        response = requests.post(url=config.PC_API_URL["device"], data=params, timeout=60)
        response_json: dict = response.json()

        if response_json.get("msg") == "No Data Found":
            return
        self.master_id: int = response_json.get("master_id")
        self.model: str = response_json.get("Model")
        self.memory: str = response_json.get("Memory")
        self.serial: str = response_json.get("Serial")
        self.esn: str = response_json.get("ESN")
        self.failed: list[str] = response_json.get("Failed").split(",")
        self.failed = set(self.failed) - set(self.blacklist)
        self.passed: list[str] = response_json.get("Passed").split(",")
        self.failed = set(self.failed) - set(self.blacklist)
        self.imei: int = response_json.get("IMEI")
        self.carrier: str = response_json.get("Carrier")
        self.color: str = response_json.get("Color")
        self.first_tested: datetime = datetime.strptime(response_json.get("DeviceCreatedDate"), "%Y-%m-%d %H:%M:%S")
        self.battery_cycle_count: int = response_json.get("BatteryCycle")
        self.battery_health_percentage: int = response_json.get("BatteryDesignMaxCapacity")
        self.unlock_status: str = response_json.get("UnlockStatus")
        self.parts_status = json.loads(response_json.get("Parts"))["Remarks"]
        self.success = True

    def __str__(self) -> str:
        if not self.success:
            return "No results"
        failed_string = "Failed:\n\t" + "\n\t".join(self.failed)
        passed_string = "Passed:\n\t" + "\n\t".join(self.passed)

        print_string = (
            f"{self.model} {self.color} {self.memory}\n"
            + f"ESN is {self.esn}\n{self.carrier} {self.imei}\n"
            + f"First tested {self.first_tested:%b %d %Y}\n"
            + f"Battery cycle count: {self.battery_cycle_count} at {self.battery_health_percentage}%\n"
            + f"\n{passed_string}\n{failed_string}\n"
            + f"Parts: {self.parts_status}"
        )
        return print_string
