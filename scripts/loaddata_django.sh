echo '========== LOAD DEFAULT CRAWLERS DATA'
docker exec -it pcts-crawlers-api /bin/bash -c \
"cd pcts_crawlers_api && python manage.py loaddata \
crawlers/fixtures/crawlers.json"
