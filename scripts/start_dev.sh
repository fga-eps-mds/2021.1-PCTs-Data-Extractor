#!/bin/bash

echo '========== CHECKING FOR UNINSTALLED PKGs AND INSTALLING'
pip install -r requirements.txt

echo '========== CHANGE TO API DIR'
cd pcts_scrapers_api

echo '========== MAKING MIGRATIONS'
python manage.py makemigrations

echo '========== RUNNING MIGRATIONS'
python manage.py migrate

echo '========== RUNNING SERVER'
python manage.py runserver 0.0.0.0:8002
