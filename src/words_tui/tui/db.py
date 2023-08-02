import datetime

from peewee import DatabaseProxy, DateTimeField, Model, SqliteDatabase, TextField

database_proxy = DatabaseProxy()


class BaseModel(Model):
    class Meta:
        database = database_proxy


class Post(BaseModel):
    content = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)


def init_db(db_path: str):
    db = SqliteDatabase(db_path)
    database_proxy.initialize(db)

    db.connect()
    db.create_tables([Post])
