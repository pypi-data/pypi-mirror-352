import datetime

from sankalp.db_connecter.base_model import BaseModel
from sankalp.models.priority import Priority
from sankalp.models.status import Status
from peewee import CharField, DateTimeField, AutoField, IntegerField, DoubleField


class Task(BaseModel):
    id = AutoField()
    title = CharField(max_length=255)
    description = CharField(max_length=1024, null=True)
    priority = IntegerField(choices=[(p.value, p.name) for p in Priority])
    status = IntegerField(choices=[(s.value, s.name) for s in Status])
    due_at = DateTimeField(
        default=lambda: datetime.datetime.now() + datetime.timedelta(hours=24)
    )
    required_time = DoubleField(
        default=1, help_text="Estimated time to complete the task in hours"
    )
    allocated_time = DoubleField(
        default=0, help_text="Time allocated to the task in hours"
    )
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    @property
    def is_active(self) -> bool:
        """
        Check if the task is active based on its status.
        """
        return Status(self.status).is_active()

    @property
    def status_name(self):
        return Status(self.status).name

    @property
    def priority_name(self):
        return Priority(self.priority).name
