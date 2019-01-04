import unittest
import datetime
from functools import wraps

from peewee import *

db = None

if __name__ == "__main__":
    db = SqliteDatabase(':memory:')
else:
    db = SqliteDatabase('work_log.db')



class Task(Model):
    name = CharField(max_length=255)
    notes = TextField()
    duration = TimeField()
    timestamp = DateField(default=datetime.datetime.now)
    
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
    return Task.select(Task.name).group_by(Task.name)

@to_dictionary
def NAMES_MATCHING(name):
    return Task.select(Task.name).where(Task.name.contains(name)).group_by(Task.name)

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


class CreateTests(unittest.TestCase):
    TEST_TASK = {
        "name": "nic", 
        "notes": "These are some notes", 
        "duration": 6
    }

    def setUp(self):
        db.connect()
        db.create_tables([Task])
    
    def tearDown(self):
        db.close()

    def test_CREATE_TASK(self):
        CREATE_TASK(self.TEST_TASK)
        task = Task.select().dicts()[0]
        self.assertEqual(task['id'], 1)
        self.assertEqual(task['name'], self.TEST_TASK['name'])
        self.assertEqual(task['notes'], self.TEST_TASK['notes'])
        self.assertEqual(task['duration'], self.TEST_TASK['duration'])
        self.assertEqual(task['timestamp'], datetime.date.today())


class QueryTests(unittest.TestCase):
    TEST_NAMES = ["nic", "nicolas", "tonia", "dave"]
    TEST_TASKS = [
        { "name": "nic", "notes": "incomplete notes these are", "duration": 2 },
        { "name": "nic", "notes": "a letter I never sent", "duration": 6 },
        { "name": "nicolas", "notes": "bile", "duration": 1 },
        { "name": "tonia", "notes": "these are some todo lists", "duration": 3 },
        { "name": "tonia", "notes": "javascript notes", "duration": 6 },
        { "name": "dave", "notes": "these are some musings", "duration": 2 },
    ]
    def setUp(self):
        db.connect()
        db.create_tables([Task])
        for task in self.TEST_TASKS:
            CREATE_TASK(task)
    
    def tearDown(self):
        db.close()
    
    def test_ALL_TASKS(self):
        tasks = ALL_TASKS()
        for idx, task in enumerate(tasks):
            self.assertEqual(task['id'], idx + 1)
            self.assertEqual(task['name'], self.TEST_TASKS[idx]['name'])
            self.assertEqual(task['notes'], self.TEST_TASKS[idx]['notes'])
            self.assertEqual(task['duration'], self.TEST_TASKS[idx]['duration'])
            self.assertEqual(task['timestamp'], datetime.date.today())
    
    def test_ALL_NAMES(self):
        names = ALL_NAMES()
        self.assertEqual(len(names), 4)
        for idx, name in enumerate(names):
            self.assertIn(name['name'], self.TEST_NAMES)

    def test_NAMES_MATCHING(self):
        names = NAMES_MATCHING("nic")
        self.assertEqual(len(names), 2)
        self.assertNotEqual(names[0], names[1])
        for idx, name in enumerate(names):
            self.assertIn(name['name'], ["nic", "nicolas"])
    
    def test_ALL_DATES(self):
        dates = ALL_DATES()
        self.assertEqual(len(dates), 1)
        self.assertNotEqual(dates[0], datetime.date.today())
    
    def test_TASKS_WITH_DURATION(self):
        tasks = TASKS_WITH_DURATION(6)
        self.assertEqual(len(tasks), 2)
        self.assertNotEqual(tasks[0]['name'], tasks[1]['name'])
        for idx, task in enumerate(tasks):
            self.assertIn(task['name'], ["tonia", "nic"])
    
    def test_TASK_WITH_ID(self):
        tasks = TASK_WITH_ID(6)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['name'], "dave")
        self.assertEqual(tasks[0]['notes'], self.TEST_TASKS[5]['notes'])

    def test_TASKS_WITH_DATE_returns_none_for_yesterday(self):
        tasks = TASKS_WITH_DATE(datetime.date.today() - datetime.timedelta(days=1))
        self.assertEqual(len(tasks), 0)

    def test_TASKS_WITH_DATE_returns_all_for_today(self):
        tasks = TASKS_WITH_DATE(datetime.date.today() - datetime.timedelta(days=0))
        self.assertEqual(len(tasks), 6)
    
    def test_TASKS_CONTAINING(self):
        tasks = TASKS_CONTAINING("these")
        self.assertEqual(len(tasks), 3)
        self.assertSetEqual(
            set(map(lambda x: x['id'], tasks)), 
            { 1, 4, 6 }
        )

if __name__ == "__main__":
    unittest.main()