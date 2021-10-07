
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import utc
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from threading import Thread
import time

jobstores = {

    'default': SQLAlchemyJobStore(url='sqlite:///db.sqlite3')
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

# scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
scheduler = BlockingScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)

def my_job(job_id):
    print(f"Execucao Job {job_id}")

def add_jobs(jobs_number):
    for job_id in range(jobs_number):

        print("Get JOB:", scheduler.get_job(job_id))
        if scheduler.get_job(job_id):
            print(f"Removing job {job_id}")
            scheduler.remove_job(job_id)

            # Update Job ID
            # scheduler.modify_job(my_job, trigger='cron', args=[job_id], second="*/5", id=str(job_id))
        print(f"Add job {job_id}")
        scheduler.add_job(my_job, trigger='cron', args=[job_id], second="*/5", id=str(job_id))

        time.sleep(5)

t = Thread(target=add_jobs, args=(10,))
t.start()

# scheduler.add_job(my_job, trigger='cron', args=[1], second="*/5")
scheduler.start()
