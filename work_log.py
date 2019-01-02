#!/usr/bin/env python3

import re
import sys
import datetime
from collections import OrderedDict
from functools import wraps, partial

import menuize
from menuize import list_print, line_input, multiline_input, numerical_input, confirmed, clear_screen, pause
import peewee as pw

db = pw.SqliteDatabase('work_log.db')

class Task(pw.Model):
    name = pw.CharField(max_length=255)
    notes = pw.TextField()
    duration = pw.DateTimeField()
    timestamp = pw.DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        database = db

messages = {
    "prompt_name": "Enter your name, then press enter",
    "prompt_notes": "Enter any notes on the job. Press ctrl+d when finished.\n",
    "prompt_duration": "Enter a duration for the job in hours (whole numbers only please)",
}

confirm_add = partial(confirmed, confirm_msg="Save task?")
prompt_name = partial(line_input, prompt=messages["prompt_name"], name="name")
prompt_notes = partial(multiline_input, prompt=messages["prompt_notes"], name="notes")
prompt_duration = partial(numerical_input, prompt=messages["prompt_duration"], name="duration")

@menuize.option(func_list=[clear_screen, prompt_name, prompt_notes, prompt_duration, confirm_add, "this"])
def add_task(*args, **kwargs):
    """add a task"""
    if kwargs['confirmation']:
        Task.create(**kwargs['input'])
    return kwargs

def initialize():
    db.connect()
    db.create_tables([Task], safe=True)

if __name__ == '__main__':    
    initialize()
    options = OrderedDict([
        ('a', add_task),
    ])
    
    work_log = menuize.Init(
        title="Welcome to the WorkLog!\n\n",
        options=options,
        prompt_string = "What would you like to do?\n(Enter either {option_list}, or q to quit)",
        exit_text="Thanks for using the WorkLog!", 
    )

    try:
        work_log.menu(callback=lambda func: func())
    except SystemExit as err:
        print(err)
        db.close()