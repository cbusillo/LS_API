"""IPSW class for downloading firmwares from Apple"""
import os
from typing import List, Any
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
import requests
from kivy.uix.button import Button
from shiny_api.modules.connect_ls import get_data


print(f"Importing {os.path.basename(__file__)}...")

IPSW_PATH = ["iPad Software Updates", "iPhone Software Updates", "iPod Software Updates"]


@dataclass
class Firmware:
    """Class for each firmware version"""

    identifier: str
    version: str
    buildid: str
    sha1sum: str
    md5sum: str
    sha256sum: str
    filesize: int
    url: str
    release_date: date
    upload_date: date
    signed: bool

    @staticmethod
    def from_dict(obj: Any) -> "Firmware":
        """Firmware class from ipsw.me"""
        _identifier = obj.get("identifier")
        _version = obj.get("version")
        _buildid = obj.get("buildid")
        _sha1sum = obj.get("sha1sum")
        _md5sum = obj.get("md5sum")
        _sha256sum = obj.get("sha256sum")
        _filesize = obj.get("filesize")
        _url = obj.get("url")
        _release_date = obj.get("releasedate")
        _upload_date = obj.get("uploaddate")
        _signed = obj.get("signed")
        return Firmware(
            _identifier,
            _version,
            _buildid,
            _sha1sum,
            _md5sum,
            _sha256sum,
            _filesize,
            _url,
            _release_date,
            _upload_date,
            _signed,
        )


@dataclass
class Devices:
    """Class describing devices from ipsw.me"""

    name: str
    identifier: str
    boardconfig: str
    platform: str
    cpid: str
    bdid: str
    firmwares: Firmware
    newest_firmware_url: str
    local_path: str

    @staticmethod
    def from_dict(obj: Any) -> "Devices":
        """Load devices object from dict"""
        _name = str(obj.get("name"))
        _identifier = str(obj.get("identifier"))
        _boardconfig = str(obj.get("boardconfig"))
        _platform = str(obj.get("platform"))
        _cpid = str(obj.get("cpid"))
        _bdid = str(obj.get("bdid"))
        response = get_data(f"https://api.ipsw.me/v4/device/{_identifier}")
        _firmwares = [Firmware.from_dict(y) for y in response.json()["firmwares"]]
        _local_path = str(obj.get("local_path"))
        return Devices(_name, _identifier, _boardconfig, _platform, _cpid, _bdid, _firmwares, "", _local_path)

    @staticmethod
    def get_devices(caller: Button) -> "List[Devices]":
        """Load Apple firmwares into IPSW list"""
        for path in IPSW_PATH:
            directory = str(f"{Path.home()}/Library/iTunes/{path}")
            Path(directory).mkdir(parents=True, exist_ok=True)
            for file in Path(directory).glob("**/*.tmp"):
                file.unlink()
        response = get_data("https://api.ipsw.me/v4/devices", current_params={"keysOnly": True})
        devices: List[Devices] = []
        for device in response.json():
            output = f'{device["name"]}'
            caller.text = f"{caller.text.split(chr(10))[0]}\n{output}"
            print(f"{output: <60}", end="\r")
            for path in IPSW_PATH:
                if device["name"].split()[0].lower() in path.lower():
                    device["local_path"] = f"{str(Path.home())}/Library/iTunes/{path}/"
                    devices.append(Devices.from_dict(device))

        for device in devices:
            newest_firmware_date = ""
            for firmware in device.firmwares:
                if firmware.upload_date > newest_firmware_date:
                    device.newest_firmware_url = firmware.url
                    newest_firmware_date = firmware.upload_date
            for firmware in device.firmwares:
                if firmware.upload_date == newest_firmware_date:
                    local_file = device.local_path + os.path.basename(urlparse(firmware.url).path)
                    # label.set(local_file)
                    caller.text = f"{caller.text.split(chr(10))[0]}\n{local_file}"
                    print(local_file, end="\r")
                    if not Path(local_file).exists():
                        with requests.get(firmware.url, stream=True, timeout=60) as response:
                            response.raise_for_status()
                            with open(local_file + ".tmp", "wb") as ipsw_file:
                                for chunk in response.iter_content(chunk_size=8192):
                                    ipsw_file.write(chunk)
                            Path(local_file + ".tmp").rename(local_file)
                else:
                    Path(device.local_path + os.path.basename(urlparse(firmware.url).path)).unlink(missing_ok=True)

        return devices
