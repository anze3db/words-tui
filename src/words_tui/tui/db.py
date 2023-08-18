import datetime
import json
import time

from peewee import (
    DatabaseProxy,
    DateTimeField,
    DoubleField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
    TextField,
)

database_proxy = DatabaseProxy()


class BaseModel(Model):
    class Meta:
        database = database_proxy


class JSONField(TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)


class Post(BaseModel):
    content = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)


class PostStats(BaseModel):
    post = ForeignKeyField(Post, backref="stats")

    words_written = IntegerField(default=0)
    words_deleted = IntegerField(default=0)
    pauses = IntegerField(default=0)
    time_writing = DoubleField(default=0)

    writing_time_until_goal = DoubleField(null=True)

    per_minute = JSONField(
        default=lambda: {
            "0": {
                "words_written": 0,
                "words_deleted": 0,
                "pauses": 0,
            }
        }
    )


class Settings(BaseModel):
    key = TextField()
    value = TextField()


def get_posts() -> list[Post]:
    return list(Post.select().order_by(Post.created_date.desc()))


def get_settings() -> Settings:
    return Settings.get(Settings.key == "words_per_day")


def init_db(db_path: str):
    db = SqliteDatabase(db_path)
    database_proxy.initialize(db)

    db.connect()
    db.create_tables([Post, PostStats, Settings])

    # Initialize settings:
    Settings.get_or_create(key="words_per_day", defaults={"value": "300"})
