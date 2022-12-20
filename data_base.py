from peewee import SqliteDatabase, Model, IntegerField, DateTimeField, TextField
import datetime as dt

db = SqliteDatabase('users.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    tg_id = IntegerField(default=0)
    time = DateTimeField(default=dt.datetime.now())
    ref = IntegerField(default=0)


db.connect()
db.create_tables([User])
