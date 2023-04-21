"""Connect to RingCentral API"""
from subprocess import Popen, PIPE
import logging
import socket
from shiny_app.classes.config import Config


def get_user_from_host(hostname: str) -> str:
    """return user and hostname from current remote ip"""
    host_to_user = {
        "chris-mbp": "cbusillo",
        "localhost": "cbusillo",
        "secureerase": "tech",
        "cornerwhinymac2": "home",
        "counter-right": "home",
    }

    username = host_to_user[hostname.lower()]
    return username


def send_message_ssh(phone_number: str, message: str, ip_address: str = "", hostname: str = ""):
    """Run Applescript to open RingCentral serach for phone number and load message"""
    if ip_address != "":
        hostname = socket.gethostbyaddr(ip_address)[0]

    with open(
        f"{Config.SCRIPT_DIR}/applescript/rc_search_by_number.applescript",
        encoding="utf8",
    ) as file:
        script_source: str = file.read()

    script_source = script_source.replace("{phone_number}", phone_number)
    script_source = script_source.replace("{message}", message)
    username = get_user_from_host(hostname)

    with Popen(
        ["ssh", f"{username}@{hostname}", "osascript", "-"],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
    ) as popen:
        popen_output = popen.communicate(bytes(script_source, encoding="utf8"))
        logging.info(popen_output)


if __name__ == "__main__":
    send_message_ssh("7578181657", "Test message", "localhost")
