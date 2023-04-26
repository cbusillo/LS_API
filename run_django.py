#!/usr/bin/env python3.11
"""File to run django server"""
import sys
import os
import logging
import subprocess
from pathlib import Path
from shiny_app.classes.config import Config
from shiny_app.modules.shiny_networking import is_host_available, scp_file_from_host


def start_django_server():
    """Setup logging, get updated certificates, and start django server"""
    logging.basicConfig(level=logging.INFO)

    if is_host_available(Config.CERTIFICATE_SERVER_HOSTNAME):
        for file_name in ["cert.pem", "privkey.pem", "fullchain.pem"]:
            local_file_name = ".shiny/secret." + file_name
            with open(Path.home() / local_file_name, "wb") as local_file:
                remote_file = scp_file_from_host(
                    Config.CERTIFICATE_SERVER_HOSTNAME,
                    Config.CERTIFICATE_SERVER_FILE + file_name,
                )
                if remote_file:
                    local_file.write(remote_file)
    path = "/usr/local/bin:/opt/homebrew/bin/"
    print(subprocess.run(["pkill", "-f", "stunnel"], check=False))
    print(subprocess.Popen(["/usr/bin/env", "-P", path, "poetry", "run", "python", "run_django.py", "migrate"], shell=False))

    print(subprocess.Popen(["/usr/bin/env", "-P", path, "stunnel", "shiny_app/config/stunnel.ini"], shell=False))
    main()


def main():
    """Run administrative tasks."""
    os.environ.setdefault(key="DJANGO_SETTINGS_MODULE", value="shiny_app.django_server.settings")
    try:
        from django.core.management import execute_from_command_line  # pylint: disable=import-outside-toplevel
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    if len(sys.argv) == 1:
        execute_from_command_line(
            [
                sys.argv[0],
                "runserver",
                "0.0.0.0:8000",
            ]
        )

    else:
        execute_from_command_line(sys.argv)


if __name__ == "__main__":
    start_django_server()
