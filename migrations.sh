#!/bin/bash

if [ $1 = "init" ]
then
    echo "Initializing migrations"
    find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
    find . -path "*/migrations/*.pyc" -delete
    rm ~/.shiny/db.sqlite3

fi

python shiny_app/modules/django_server.py makemigrations
python shiny_app/modules/django_server.py migrate

