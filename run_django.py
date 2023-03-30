#!/usr/bin/env python
"""File to run django server"""
import logging
from pathlib import Path
from shiny_api.modules.django_server import main
from shiny_api.modules.load_config import Config
from shiny_api.modules.shiny_networking import is_host_available, scp_file_from_host


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if not is_host_available(Config.CERTIFICATE_SERVER_HOSTNAME):
        main()

    for file_name in ["cert.pem", "privkey.pem"]:
        local_file_name = ".secret." + file_name
        with open(Path.home() / local_file_name, "wb") as local_file:
            local_file.write(
                scp_file_from_host(
                    Config.CERTIFICATE_SERVER_HOSTNAME,
                    Config.CERTIFICATE_SERVER_FILE + file_name,
                )
            )

    main()
