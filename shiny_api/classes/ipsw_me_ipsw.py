"""IPSW class for downloading firmwares from Apple"""
import os
from typing import Any, Self
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
import requests
from kivy.uix.button import Button
from shiny_api.modules.connect_ls import get_data


print(f"Importing {os.path.basename(__file__)}...")

IPSW_PATH = ["iPad Software Updates", "iPhone Software Updates", "iPod Software Updates"]
IPSW_ME_API_URL = {"device": "https://api.ipsw.me/v4/device/", "devices": "https://api.ipsw.me/v4/devices"}


@dataclass
class Firmware:
    """Class for each firmware version"""

    def __init__(self, obj: Any):
        """Firmware class from ipsw.me"""
        self.identifier = obj.get("identifier")
        self.version = obj.get("version")
        self.buildid = obj.get("buildid")
        self.sha1sum = obj.get("sha1sum")
        self.md5sum = obj.get("md5sum")
        self.sha256sum = obj.get("sha256sum")
        self.filesize = obj.get("filesize")
        self.url = obj.get("url")
        self.release_date = obj.get("releasedate")
        self.upload_date = obj.get("uploaddate")
        self.signed = obj.get("signed")


@dataclass
class Device:
    """Class describing devices from ipsw.me"""

    def __init__(self, obj: Any):
        """Load devices object from dict"""
        self.name = str(obj.get("name"))
        self.identifier = str(obj.get("identifier"))
        self.boardconfig = str(obj.get("boardconfig"))
        self.platform = str(obj.get("platform"))
        self.cpid = str(obj.get("cpid"))
        self.bdid = str(obj.get("bdid"))
        response = get_data(f"{IPSW_ME_API_URL['device']}{self.identifier}")
        self.firmwares = [Firmware(y) for y in response.json()["firmwares"]]
        self.local_path = str(obj.get("local_path"))

    @staticmethod
    def _get_devices(caller: Button = None) -> list[Self]:
        """Load Apple firmwares into IPSW list"""

        response = get_data(f"{IPSW_ME_API_URL['devices']}", current_params={"keysOnly": True})
        devices: list[Device] = []
        for device in response.json():
            output = f'{device["name"]}'
            caller.text = f"{caller.text.split(chr(10),maxsplit=1)[0]}\n{output}"
            print(f"{output: <60}", end="\r")
            for path in IPSW_PATH:
                if device["name"].split()[0].lower() in path.lower():
                    device["local_path"] = f"{str(Path.home())}/Library/iTunes/{path}/"
                    devices.append(Device(device))

        return devices

    def download_firmware(self, caller: Button = None) -> None:
        """Download firmware from ipsw.me"""
        for firmware in self.firmwares:
            local_file = self.local_path + os.path.basename(urlparse(firmware.url).path)
            if not firmware.signed:
                Path(local_file).unlink(missing_ok=True)
                continue

            output = f"Downloading {firmware.identifier} {firmware.version}..."
            caller.text = f"{caller.text.split(chr(10))[0]}\n{output}"
            print(f"{output: <60}", end="\r")
            if not Path(local_file).is_file():
                response = requests.get(firmware.url, stream=True, timeout=60)
                with open(f"{local_file}.tmp", "wb") as firmware_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            firmware_file.write(chunk)
                Path(local_file + ".tmp").rename(local_file)
            else:
                print(f"{local_file} already exists")

    @classmethod
    def download_all_firmwares(cls, caller: Button = None) -> None:
        """Download all firmwares from ipsw.me"""
        cls.delete_temp_firmwares()
        devices = Device._get_devices(caller)
        for device in devices:
            device.download_firmware(caller)

    @staticmethod
    def delete_temp_firmwares() -> None:
        """delete firmwares that did not finish downloading"""
        for path in IPSW_PATH:
            directory = str(f"{Path.home()}/Library/iTunes/{path}")
            Path(directory).mkdir(parents=True, exist_ok=True)
            for file in Path(directory).glob("**/*.tmp"):
                file.unlink()
