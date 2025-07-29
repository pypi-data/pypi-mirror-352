import datetime
from typing import Optional

from peewee import AutoField, DateTimeField, CharField

from sankalp.db_connecter.base_model import BaseModel


class Focus(BaseModel):
    id = AutoField()
    description = CharField(max_length=1024, null=True)
    start_time = DateTimeField(default=datetime.datetime.now)
    end_time = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    @property
    def is_active(self):
        return self.end_time is None or self.end_time > datetime.datetime.now()

    @classmethod
    def get_active_focus_session(cls) -> Optional["Focus"]:
        """
        Get the currently active focus session.
        """
        try:
            focus = Focus.get(Focus.end_time.is_null(True))
            return focus
        except Exception as e:
            return None
