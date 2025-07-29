from peewee import Model
from sankalp.db_connecter import db


class BaseModel(Model):
    class Meta:
        database = db
