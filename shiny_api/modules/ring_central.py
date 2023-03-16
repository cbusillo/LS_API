"""Connect to RingCentral API"""
import os
from subprocess import Popen, PIPE
from shiny_api.modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")


def send_message_ssh(phone_number: str, message: str):
    """Run Applescript to open RingCentral serach for phone number and load message"""
    with open(
            f"{config.SCRIPT_DIR}/applescript/rc_search_by_number.applescript", encoding="utf8") as file:
        script_source: str = file.read()

    script_source = script_source.replace("{phone_number}", phone_number)
    script_source = script_source.replace("{message}", message)
    popen = Popen(['ssh', 'cbusillo@localhost', 'osascript', '-'],
                  stdin=PIPE, stdout=PIPE, stderr=PIPE)

    popen.communicate(bytes(script_source, encoding="utf8"))


if __name__ == "__main__":
    send_message_ssh("7578181657", "Test message")
