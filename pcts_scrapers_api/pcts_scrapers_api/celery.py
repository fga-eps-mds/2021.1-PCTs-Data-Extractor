import os

from celery import Celery
from celery import shared_task
from celery.schedules import crontab


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pcts_scrapers_api.settings')

app = Celery('pcts_scrapers_api')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, name="debug_task")
def debug_task(self):
    print(f'Request: {self.request!r}')


@app.task
def add(x, y):
    return x + y


@shared_task(name="hello")
def hello():
    return "Hello World!"
