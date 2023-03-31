#!/usr/bin/env python
"""File to run django server"""
import logging
from pathlib import Path
import shiny_api.modules.django_server as django_server
from shiny_api.modules.load_config import Config
from shiny_api.modules.shiny_networking import is_host_available, scp_file_from_host


def start_django_server():
    logging.basicConfig(level=logging.INFO)

    if not is_host_available(Config.CERTIFICATE_SERVER_HOSTNAME):
        django_server.main()
        exit()

    for file_name in ["cert.pem", "privkey.pem"]:
        local_file_name = ".secret." + file_name
        with open(Path.home() / local_file_name, "wb") as local_file:
            local_file.write(
                scp_file_from_host(
                    Config.CERTIFICATE_SERVER_HOSTNAME,
                    Config.CERTIFICATE_SERVER_FILE + file_name,
                )
            )

    django_server.main()


if __name__ == "__main__":
    start_django_server()
