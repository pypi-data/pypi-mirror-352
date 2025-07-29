import datetime
import signal
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from scheduler_service.reminder_scheduler import notify_reminder, sync_db
import logging

logging.basicConfig(level=logging.INFO)

DB_URI = "postgresql://postgres:password@localhost:5432/sankalp_db"
jobstores = {"default": SQLAlchemyJobStore(url=DB_URI)}
executors = {
    "default": ThreadPoolExecutor(8),
}
job_defaults = {"coalesce": False, "max_instances": 3}
scheduler = BlockingScheduler()

scheduler.configure(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone="Asia/Kolkata",
)

scheduler.add_job(
    notify_reminder,
    "interval",
    minutes=1,
    id="notify_reminder",
    next_run_time=datetime.datetime.now(),
    misfire_grace_time=30,
    replace_existing=True,
)
scheduler.add_job(
    sync_db,
    "interval",
    minutes=30,
    id="sync_db",
    next_run_time=datetime.datetime.now(),
    misfire_grace_time=5 * 60,
    replace_existing=True,
)


def shutdown_scheduler(signum, frame):
    logging.info("Shutting down scheduler gracefully...")
    scheduler.shutdown(wait=True)
    sys.exit(0)


# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, shutdown_scheduler)
signal.signal(signal.SIGTERM, shutdown_scheduler)

scheduler.start()
