#!/bin/bash

echo '========== CHANGE TO API DIR'
cd pcts_crawlers_api

echo '========== START CELERY'
celery -A pcts_crawlers_api worker -l INFO
