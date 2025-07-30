from typing import Optional

from peewee import AutoField, DateTimeField, IntegerField, ForeignKeyField
from sankalp.db_connecter.base_model import BaseModel
from sankalp.models import Task, Status
import datetime


class Reminder(BaseModel):
    id = AutoField()
    task = ForeignKeyField(Task, backref="reminders", on_delete="CASCADE")
    remind_at = DateTimeField(help_text="The time to remind the user about the task")

    @property
    def is_active(self) -> bool:
        """
        Check if the reminder is active based on the current time.
        """
        return self.remind_at > datetime.datetime.now() and Status(self.task.status).is_active()  # type: ignore

    @classmethod
    def get_active_reminders(
        cls, max_duration: Optional[datetime.timedelta] = None
    ) -> list["Reminder"]:
        """
        Get all active reminders.
        """
        if max_duration:
            return list(
                cls.select()
                .join(Task)
                .where(cls.task.status << Status.get_active_status())
                .where(cls.remind_at > datetime.datetime.now())
                .where(cls.remind_at <= datetime.datetime.now() + max_duration)
                .order_by(cls.remind_at)
            )
        return list(
            cls.select()
            .join(Task)
            .where(cls.task.status << Status.get_active_status())
            .where(cls.remind_at > datetime.datetime.now())
            .order_by(Reminder.remind_at)
        )  # type: ignore


class ReminderSerialized:
    """
    Serialized representation of a Reminder.
    """

    id: int
    task_id: int
    task_title: str
    remind_at: datetime.datetime

    def __init__(self, reminder: Reminder):
        self.id = reminder.id
        self.task_id = reminder.task.id
        self.task_title = reminder.task.title
        self.remind_at = reminder.remind_at

    def is_active(self) -> bool:
        """
        Check if the reminder is active.
        """
        return self.remind_at > datetime.datetime.now()
