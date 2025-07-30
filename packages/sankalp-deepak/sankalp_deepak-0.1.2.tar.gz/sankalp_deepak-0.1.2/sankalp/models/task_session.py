import datetime

from peewee import AutoField, ForeignKeyField, DoubleField, DateTimeField
from sankalp.db_connecter.base_model import BaseModel
from sankalp.models import Task, Focus


class TaskSession(BaseModel):
    id = AutoField()
    task = ForeignKeyField(Task, backref="sessions")
    focus = ForeignKeyField(Focus, backref="sessions")
    duration = DoubleField(default=0)
    created_at = DateTimeField(default=datetime.datetime.now)
