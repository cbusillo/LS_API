"""Connect to sickw and return a SickwResults object with data from serial_number and service """
import os
import applescript
from shiny_api.modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")


def send_message(phone_number: str, message: str):
    """Run Applescript to open RingCentral serach for phone number and load message"""
    with open(f"{config.SCRIPT_DIR}/applescript/rc_search_by_number.applescript", encoding="utf8") as file:
        script_source: str = file.read()

    script_source = script_source.replace("{phone_number}", phone_number)
    script_source = script_source.replace("{message}", message)
    script = applescript.AppleScript(script_source)
    script.run()


if __name__ == "__main__":
    send_message("7578181657", "Test message")
