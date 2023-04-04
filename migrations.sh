#!/bin/bash
python shiny_api/modules/django_server.py makemigrations
python shiny_api/modules/django_server.py migrate

