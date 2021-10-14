#!/bin/bash

echo '========== CHANGE TO API DIR'
cd pcts_scrapers_api

echo '========== START CELERY WORKER + SCHEDULER + WEBVIEW FLOWER'
celery worker --app=pcts_scrapers_api --loglevel=INFO --beat & celery flower --app=pcts_scrapers_api --loglevel=ERROR --persistent=True
