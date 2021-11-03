#!/bin/bash

echo '========== CHECKING FOR UNINSTALLED PKGs AND INSTALLING'
pip install -r requirements.txt

echo '========== CHANGE TO API DIR'
cd pcts_crawlers_api

echo '========== MAKING MIGRATIONS'
python manage.py makemigrations

echo '========== RUNNING MIGRATIONS'
python manage.py migrate

echo '========== ENSURING ADMIN USER'
python manage.py ensure_adminuser --username=$DJANGO_SUPERUSER_USERNAME \
    --email=$DJANGO_SUPERUSER_EMAIL \
    --password=$DJANGO_SUPERUSER_PASSWORD

echo '========== LOAD DEFAULT CRAWLERS DATA'
python manage.py loaddata crawlers/fixtures/crawlers.json

echo '========== LOAD DEFAULT KEYWORDS DATA'
python manage.py loaddata keywords/fixtures/keywords.json

echo '========== RUNNING SERVER'
python manage.py runserver 0.0.0.0:8002
