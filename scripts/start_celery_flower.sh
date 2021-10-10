#!/bin/bash

echo '========== CHANGE TO API DIR'
cd pcts_scrapers_api

echo '========== START CELERY'
celery -A proj flower
