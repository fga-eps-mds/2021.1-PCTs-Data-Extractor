import os

from celery import Celery
from celery import shared_task
from celery.schedules import crontab

from scrapers import tasks


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pcts_scrapers_api.settings')

app = Celery('pcts_scrapers_api')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, name="debug_task")
def debug_task(self):
    print(f'Request: {self.request!r}')


@shared_task
def add(x, y):
    return x + y


@shared_task(name="hello")
def hello():
    return "Hello World!"


# ============================= AUTO CREATE SCHEDULERS ON STARTUP
@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(
        30.0,
        add.s(y=2, x=1),
        name="add",
        expires=10,
    )


@app.on_after_configure.connect
def setup_periodic_scrapers(sender: Celery, **kwargs):
    KEYWORDS = [
        "povos e comunidades tradicionais",
        "quilombolas",
    ]

    # INCRA SCRAPER
    sender.add_periodic_task(
        crontab(minute='0', hour='4', day_of_week='*',
                day_of_month='*', month_of_year='*'),
        tasks.incra_scraper_group.subtask(keywords=KEYWORDS),
        name="incra_scraper_group",
    )

    # MPF SCRAPER
    sender.add_periodic_task(
        crontab(minute='0', hour='5', day_of_week='*',
                day_of_month='*', month_of_year='*'),
        tasks.mpf_scraper.subtask(keywords=KEYWORDS),
        name="mpf_scraper",
    )
