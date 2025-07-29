import datetime
import logging
import pync  # type: ignore
from utils.cache_utils import MemoryCache
from db_connecter import db
from models import Reminder
from models.reminder import ReminderSerialized


logger = logging.getLogger(__name__)


def notify(message):
    pync.notify(message, title="Sankalp")


cache = MemoryCache()


def notify_reminder():
    reminders = cache.get("reminders") or list()
    logger.info(f"Found {len(reminders)} reminders to check.")
    triggered_reminders = set()
    reminder: ReminderSerialized
    for reminder in reminders:
        if reminder.remind_at <= datetime.datetime.now():
            logger.info(
                f"Triggering reminder for task: {reminder.task_title} at {reminder.remind_at.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            notify(
                f"Reminder for Task: {reminder.task_title} at {reminder.remind_at.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            triggered_reminders.add(reminder)
    non_triggered_reminders = [
        reminder for reminder in reminders if reminder not in triggered_reminders
    ]
    cache.set("reminders", non_triggered_reminders)


def add_reminder(reminder):
    """
    Add a reminder to the cache.
    """
    reminders = cache.get("reminders") or list()
    reminders.append(reminder)
    cache.set("reminders", reminders)


def delete_reminder(reminder_id):
    """
    Delete a reminder from the cache by its ID.
    """
    reminders = cache.get("reminders") or list()
    reminders = [reminder for reminder in reminders if reminder.id != reminder_id]
    cache.set("reminders", reminders)


def sync_db():
    """
    Sync reminders from the database to the cache.
    """
    logger.info("Syncing reminders from the database to the cache.")
    db.connect()
    reminders = list(
        Reminder.get_active_reminders(max_duration=datetime.timedelta(minutes=30))
    )
    reminders_ser = [ReminderSerialized(reminder) for reminder in reminders]
    cache.set("reminders", reminders_ser)
    logger.info(f"Synced {len(reminders_ser)} reminders to the cache.")
    db.close()
