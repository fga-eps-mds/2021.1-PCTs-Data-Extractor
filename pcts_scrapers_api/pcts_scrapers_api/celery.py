import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pcts_scrapers_api.settings')

app = Celery('pcts_scrapers_api')
# app = Celery('pcts_scrapers_api', broker="amqp://guest@localhost//")

app.conf.CELERY_RESULT_BACKEND='amqp://'
# CELERY_RESULT_BACKEND='amqp://'
# app.conf.CELERY_RESULT_BACKEND = 'db+sqlite:///results.sqlite'

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
