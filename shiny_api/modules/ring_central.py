"""Connect to RingCentral API"""
import os
import socket
from subprocess import Popen, PIPE
from flask import request
from shiny_api.modules import load_config as config

print(f"Importing {os.path.basename(__file__)}...")


def get_host_user_from_ip() -> tuple[str, str]:
    HOST_TO_USER = {"chris-mbp": "cbusillo",
                    "secureerase": "tech",
                    "cornerwhinymac2": "home",
                    "countershinymac": "home"}
    hostname = socket.gethostbyaddr(request.remote_addr)[0]
    username = HOST_TO_USER[hostname.lower()]
    print(hostname)
    return hostname, username


def send_message_ssh(phone_number: str, message: str):
    """Run Applescript to open RingCentral serach for phone number and load message"""
    with open(
            f"{config.SCRIPT_DIR}/applescript/rc_search_by_number.applescript", encoding="utf8") as file:
        script_source: str = file.read()

    script_source = script_source.replace("{phone_number}", phone_number)
    script_source = script_source.replace("{message}", message)
    hostname, username = get_host_user_from_ip()
    popen = Popen(['ssh', f'{username}@{hostname}', 'osascript', '-'],
                  stdin=PIPE, stdout=PIPE, stderr=PIPE)

    print(popen.communicate(bytes(script_source, encoding="utf8")))


if __name__ == "__main__":
    send_message_ssh("7578181657", "Test message")
# imagingserver.local:8001/api/rc_send_message/?workorderID=25654
