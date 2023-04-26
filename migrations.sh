#!/bin/bash

if [ "$1" == "init" ]
then
    echo "Initializing migrations"
    find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
    find . -path "*/migrations/*.pyc" -delete
fi
if [ $# -gt 0 ]
then
    echo "adding migrations"
    for directory in ./shiny_app/django_apps/*/
    do
        if [[ $directory == *"__pycache__"* ]]
        then
            continue
        fi
        python manage_django.py makemigrations `basename $directory`
    done
fi

python manage_django.py makemigrations
python manage_django.py migrate

