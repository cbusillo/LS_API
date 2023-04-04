#!/usr/bin/env python
"""File to run django server"""
import logging
import subprocess
from pathlib import Path
import shiny_api.modules.django_server as django_server
from shiny_api.modules.load_config import Config
from shiny_api.modules.shiny_networking import is_host_available, scp_file_from_host


def start_django_server():
    """Setup logging, get updated certificates, and start django server"""
    logging.basicConfig(level=logging.INFO)

    if is_host_available(Config.CERTIFICATE_SERVER_HOSTNAME):
        for file_name in ["cert.pem", "privkey.pem", "fullchain.pem"]:
            local_file_name = ".secret." + file_name
            with open(Path.home() / local_file_name, "wb") as local_file:
                remote_file = scp_file_from_host(
                    Config.CERTIFICATE_SERVER_HOSTNAME,
                    Config.CERTIFICATE_SERVER_FILE + file_name,
                )
                if remote_file:
                    local_file.write(remote_file)
    print(subprocess.run(["pkill", "-f", "stunnel"], check=False))
    print(subprocess.Popen("python shiny_api/modules/django_server.py migrate", shell=True))

    print(subprocess.Popen("stunnel shiny_api/config/stunnel.ini", shell=True))
    django_server.main()


if __name__ == "__main__":
    start_django_server()
