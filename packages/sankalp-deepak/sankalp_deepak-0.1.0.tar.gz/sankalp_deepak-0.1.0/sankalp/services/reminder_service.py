import datetime
import json
from typing import Union, Optional
import logging
from sankalp.models import Reminder, Task

logger = logging.getLogger(__name__)


def create(task_id: int, remind_at: datetime.datetime) -> Reminder:
    """
    Create a new reminder for a task.
    """
    reminder = Reminder.create(task=task_id, remind_at=remind_at)
    return reminder


def delete(reminder_id: int) -> None:
    """
    Delete a reminder by its ID.
    """
    reminder = Reminder.get_by_id(reminder_id)
    reminder.delete_instance()


def get_reminders_for_task(task_id: int) -> list[Reminder]:
    """
    Get all reminders for a specific task.
    """
    return list(
        Reminder.select().where(Reminder.task == task_id).order_by(Reminder.remind_at)
    )


def get_active_reminders() -> list[Reminder]:
    """
    Get all active reminders.
    """
    return Reminder.get_active_reminders()


def get_all_reminders() -> list[Reminder]:
    """
    Get all reminders.
    """
    return list(Reminder.select().order_by(Reminder.remind_at))


def get_reminder_date(
    due_date: datetime.datetime, delta: Union[str, dict]
) -> datetime.datetime:
    if isinstance(delta, str):
        if delta == "half":
            return due_date - datetime.timedelta(
                seconds=(datetime.datetime.now() - due_date).total_seconds() / 2
            )
        elif delta.endswith("%"):
            percentage = float(delta[:-1]) / 100
            return due_date - datetime.timedelta(
                seconds=(datetime.datetime.now() - due_date).total_seconds()
                * percentage
            )
        else:
            raise ValueError(
                "Invalid delta string format. Use 'half', 'x%', or a dictionary."
            )
    elif isinstance(delta, dict):
        days = delta.get("days", 0)
        hours = delta.get("hours", 0)
        minutes = delta.get("minutes", 0)
        seconds = delta.get("seconds", 0)
        return due_date - datetime.timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds
        )
    else:
        raise ValueError("Invalid delta format. Must be a string or a dictionary.")


def _create_reminder_from_policy(
    task: Task, policy: Union[str, dict]
) -> Optional[Reminder]:
    reminder_ts = get_reminder_date(task.due_at, policy)  # type: ignore
    if reminder_ts < datetime.datetime.now():
        logger.warning(
            f"Reminder for task {task.id} is in the past. Skipping reminder creation."
        )
        return None
    if reminder_ts > task.due_at:
        logger.warning(
            f"Reminder for task {task.id} is after the due date. Skipping reminder creation."
        )
        return None
    if reminder_ts - datetime.datetime.now() < datetime.timedelta(minutes=30):
        logger.warning(
            f"Reminder for task {task.id} is too close to the current time. Reminder may not work as expected."
        )
    return Reminder(
        task=task, remind_at=get_reminder_date(task.due_at, policy)  # type: ignore
    )


def create_reminders_from_policy(task) -> Optional[list[Reminder]]:
    with open("reminder_policy.json") as f:
        policies = json.load(f).get(task.priority_name)
    if not policies:
        return []
    reminders = list()
    for policy in policies:
        reminder = _create_reminder_from_policy(task, policy)
        if reminder:
            logger.info(
                f"Creating reminder for task {task.id} with remind_at {reminder.remind_at}"
            )
            reminders.append(reminder)
    return (
        Reminder.bulk_create([reminder for reminder in reminders]) if reminders else []
    )
