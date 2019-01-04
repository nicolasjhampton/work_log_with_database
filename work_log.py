#!/usr/bin/env python3

from functools import partial

from menuize import (Menu, option, end, list_print, line_input, multiline_input, 
                    numerical_input, confirmed, clear_screen, choice_menu, pause)

from models import (initialize, ALL_TASKS, ALL_NAMES, ALL_DATES, CREATE_TASK, 
                    TASKS_WITH_DURATION, NAMES_MATCHING, TASK_WITH_ID, 
                    TASKS_WITH_DATE, TASKS_CONTAINING)

messages = {
    "title_name": "Select an employee:",
    "title_date": "Select a date:", 
    "prompt_name": "Enter your name, then press enter",
    "prompt_notes": "Enter any notes on the job. Press ctrl+d when finished.\n",
    "prompt_duration": "Enter a duration for the job in hours (whole numbers only please)",
    "prompt_search_choice": "Please enter a search option",
    "search_name": "Please enter an employee name",
    "search_date": "Select a date range",
    "search_phrase": "Please enter a phrase you'd like to search for",
    "search_time": "Please enter a duration in hours",
    "search_menu": "What would you like to search by?",
}

templates = {
    "name": "{name}\n",
    "timestamp": "{id}) {timestamp}\n",
    "task": """
{id} {name} {timestamp}: 
{notes}
Duration: {duration} hours
___________________________________________________
"""
}

confirm_add = partial(confirmed, confirm_msg="Save task?")
task_print = partial(list_print, item_template=templates['task'], title="")
prompt_name = partial(line_input, prompt=messages["prompt_name"], name="name")
prompt_notes = partial(multiline_input, prompt=messages["prompt_notes"], name="notes")
prompt_duration = partial(numerical_input, prompt=messages["prompt_duration"], name="duration")

def all_tasks():
    return []

def phrase_search():
    prompt_phrase = partial(line_input, prompt=messages["search_phrase"], name="phrase")
    return [clear_screen, prompt_phrase]

def time_search():
    prompt_time = partial(numerical_input, prompt=messages["search_time"], name="time")
    return [clear_screen, prompt_time]

def name_search():
    def get_employees(*args, **kwargs):
        kwargs['list'] = ALL_NAMES()
        return kwargs
    employee_print = partial(list_print, item_template=templates['name'], title=messages['title_name'])
    prompt_name = partial(line_input, prompt=messages["search_name"], name="name")
    return [clear_screen, get_employees, employee_print, prompt_name]

def date_search():
    def get_dates(*args, **kwargs):
        unnumbered = ALL_DATES()
        numbered = map(lambda x: { 'id': x[0] + 1, **x[1] }, enumerate(unnumbered))
        kwargs['list'] = list(numbered)
        return kwargs
    dates_print = partial(list_print, item_template=templates['timestamp'], title=messages['title_date'])
    prompt_date = partial(numerical_input, prompt=messages["search_date"], name="date")
    return [clear_screen, get_dates, dates_print, prompt_date]

search_options = [
    ('a', all_tasks),
    ('n', name_search),
    ('d', date_search),
    ('p', phrase_search),
    ('t', time_search)
]

search_choice = partial(choice_menu, title=messages["search_menu"], 
                        prompt=messages["prompt_search_choice"], 
                        options=search_options, name="search")

@option(func_list=[clear_screen, prompt_name, prompt_notes, prompt_duration, confirm_add, "this", end])
def add_task(*args, **kwargs):
    """add a task"""
    if kwargs['input']:
        CREATE_TASK(kwargs['input'])
    return kwargs

def grab_date_helper(obj):
    date_choice = obj['input']['date']
    date_range = obj['list'][date_choice - 1]
    return date_range['timestamp']

@option(func_list=[clear_screen, search_choice, "*", "this", clear_screen, task_print, end])
def search_tasks(*args, **kwargs):
    """search for tasks"""
    inputs = kwargs['input']
    choice = inputs['search']
    if choice == 'n':
        matches = NAMES_MATCHING(inputs['name'])
        if len(matches) < 1:
            kwargs['alert'] = "::: NO MATCHES try again :::"
            return search_tasks(**kwargs)
        elif len(matches) == 1:
            # This needs to be fixed
            # kwargs['list'] = TASK_WITH_ID(matches[0]['id'])
    if choice == 't':
        kwargs['list'] = TASKS_WITH_DURATION(inputs['time'])
    elif choice == 'd':
        kwargs['list'] = TASKS_WITH_DATE(grab_date_helper(kwargs))
    elif choice == 'p':
        kwargs['list'] = TASKS_CONTAINING(inputs['phrase'])
    else:
        kwargs['list'] = ALL_TASKS()
    return kwargs


if __name__ == '__main__':    
    db = initialize()
    options = [
        ('a', add_task),
        ('s', search_tasks),
    ]
    
    work_log = Menu(
        title="Welcome to the WorkLog!\n\n",
        options=options,
        prompt_string = "What would you like to do?\n(Enter either {option_list}, or q to quit)",
        exit_text="Thanks for using the WorkLog!", 
    )

    try:
        work_log.loop(callback=lambda func: func())
    except SystemExit as err:
        print(err)
        db.close()