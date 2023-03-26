#!/usr/bin/env python
"""File to run flask server"""
import logging
from shiny_api.modules.flask_server import start_flask_server


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    start_flask_server()
