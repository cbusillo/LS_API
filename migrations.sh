#!/bin/bash

if [ "$1" == "init" ]
then
    echo "Initializing migrations"
    find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
    find . -path "*/migrations/*.pyc" -delete
    rm ~/.shiny/db.sqlite3
fi
if [ $# -gt 0 ]
then
    echo "adding migrations"
    for directory in ./shiny_app/django_server/*/
    do
        if [[ $directory == *"__pycache__"* || $directory == *"templates"* || $directory == *"static"* ]]
        then
            continue
        fi
        python shiny_app/modules/django_server.py makemigrations `basename $directory`
    done
fi

python shiny_app/modules/django_server.py makemigrations
python shiny_app/modules/django_server.py migrate

