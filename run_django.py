#!/usr/bin/env python
"""File to run django server"""
import logging
from shiny_api.modules.django_server import main


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
