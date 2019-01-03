import unittest
import datetime
from functools import wraps

import peewee as pw

db = pw.SqliteDatabase('work_log.db')

class Task(pw.Model):
    name = pw.CharField(max_length=255)
    notes = pw.TextField()
    duration = pw.TimeField()
    timestamp = pw.DateField(default=datetime.datetime.now)
    
    class Meta:
        database = db

def initialize():
    db.connect()
    db.create_tables([Task], safe=True)
    return db

def CREATE_TASK(data):
    Task.create(**data)

def to_dictionary(func):
    @wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs).dicts()
    return inner

@to_dictionary
def ALL_TASKS():
    return Task.select()

@to_dictionary
def ALL_NAMES():
    return Task.select(Task.id, Task.name).group_by(Task.name)

@to_dictionary
def NAMES_MATCHING(name):
    return Task.select(Task.name, Task.id).where(Task.name ** name).group_by(Task.name)

@to_dictionary
def ALL_DATES():
    return Task.select(Task.timestamp).group_by(Task.timestamp)

@to_dictionary
def TASKS_WITH_DURATION(time):
    return Task.select().where(Task.duration == time)

@to_dictionary
def TASK_WITH_ID(ID):
    return Task.select().where(Task.id == ID)

@to_dictionary
def TASKS_WITH_DATE(date):
    return Task.select().where(Task.timestamp == date)

@to_dictionary
def TASKS_CONTAINING(phrase):
    return Task.select().where(Task.name.contains(phrase) | Task.notes.contains(phrase))


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        pass
    


if __name__ == "__main__":
    unittest.main()