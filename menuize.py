import re
import sys
import os
from collections import OrderedDict
from functools import wraps, reduce, partial

class EndOption(Exception):
    """Ends an option chain"""
    def __init__(self, message):
        self.message = message

def clear():
    """clears the screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause(*args, **kwargs):
    input("...   ")
    return kwargs

def clear_screen(*args, **kwargs):
    clear()
    return kwargs

def end(*args, **kwargs):
    raise EndOption("...   ")

def get_opt_name(option):
    """returns the truncated version of the option function
    
    >>> def add_entry():
    ...     pass
    ... 
    >>> get_opt_name(add_entry)
    'add'
    """
    return re.search(r'(?P<option>[\w]+)\_.*', option.__name__).group('option')

def option_titles(options):
    """returns a list of option names"""
    return [(l, get_opt_name(o)) for l, o in options.items()]

def normalize_func_list(chain_function, this):
    func_list = chain_function()
    func_list[func_list.index("this")] = this
    return func_list

def create_func_list_factory(chain_function, this):
    return partial(normalize_func_list, this=this, chain_function=chain_function)

def executor(*args, **kwargs):
    def inner(acc, cur):
        start_check = acc.__class__.__name__
        try:
            if start_check in ['function', 'partial', 'Mock']:
                acc = acc(*args, **kwargs)
            func = cur(**acc)
            return func
        except EndOption as err:
            raise 
    return inner

def exec_funcs(*args, **kwargs):
    funcs_arr = kwargs['func_list']
    return reduce(executor(*args, **kwargs), funcs_arr)

def multiline_input(*args, **kwargs):
    name = kwargs['name']
    prompt = kwargs['prompt']
    print(prompt)
    if "input" not in kwargs:
        kwargs['input'] = dict()
    kwargs['input'][name] = sys.stdin.read().strip().lower()
    print("")
    # cleanup namespaces
    del kwargs['name']
    del kwargs['prompt']
    return kwargs

def line_input(*args, **kwargs):
    name = kwargs['name']
    prompt = kwargs['prompt']
    data = input("{prompt} >>>  ".format(prompt=prompt))
    if "input" not in kwargs:
        kwargs['input'] = dict()
    kwargs['input'][name] = data.lower().strip()
    # cleanup namespaces
    del kwargs['name']
    del kwargs['prompt']
    return kwargs

def numerical_input(*args, **kwargs):
    name = kwargs['name']
    prompt = kwargs['prompt']
    data = input("{prompt} >>>  ".format(prompt=prompt))
    if "input" not in kwargs:
        kwargs['input'] = dict()
    kwargs['input'][name] = int(data.strip())
    # cleanup namespaces
    del kwargs['name']
    del kwargs['prompt']
    return kwargs

def confirmed(*args, **kwargs):
    confirm_msg = kwargs['confirm_msg']
    input_to_confirm = kwargs['input']
    kwargs['confirmation'] = True if input_to_confirm and input('\n{} [Yn]  '.format(confirm_msg)).strip().lower()[0] != "n" else False
    return kwargs

def list_string(*args, **kwargs):
    string = ""
    if 'title' in kwargs:
        string += kwargs['title']
        string += "\n\n"
    for row in kwargs['list']:
        if isinstance(row, tuple):
            string += kwargs['item_template'].format(*row)
        else:
            string += "\n"
            string += kwargs['item_template'].format(**row)
    string += "\n___________________________________________________"
    string += "\n"
    return string

def list_print(*args, **kwargs):
    print(
        list_string(**kwargs)
    )
    del kwargs['title']
    del kwargs['item_template']
    return kwargs

def print_choice_menu(**kwargs):
    kwargs = list_print(
        item_template="{}) {}\n",
        list=kwargs['option_list'],
        **kwargs
    )
    del kwargs['list']
    del kwargs['option_list']
    return kwargs

def print_alert(**kwargs):
    if 'alert' in kwargs:
        print("::: {} :::".format(kwargs['alert']))
        del kwargs['alert']
    return kwargs

def merge_option_branch(option_branch, kwargs):
    func_list = kwargs['func_list_factory']()
    wild_idx = func_list.index("*")
    func_list[wild_idx:wild_idx + 1] = option_branch
    kwargs['func_list'][:] = func_list
    return kwargs

def choice_menu(*args, **kwargs):
    options = OrderedDict(kwargs['options'])
    name = kwargs['name']
    backup = kwargs['title'], kwargs['name'], kwargs['prompt']
    kwargs = print_alert(**kwargs)
    kwargs = line_input(
        **print_choice_menu(
            option_list=option_titles(options), 
            **kwargs
        )
    )
    option = kwargs['input'][name][0]

    if option == "q":
        sys.exit("GOODBYE")
    if option not in options.keys():
        kwargs['title'], kwargs['name'], kwargs['prompt'] = backup
        kwargs['alert'] = "::: BAD INPUT  Please try again :::"
        clear()
        return choice_menu(**kwargs)

    choice_funcs = options[option]()
    return merge_option_branch(choice_funcs, kwargs)

def option(chain_function):
    """takes func_list and args"""
    def middle(func):
        @wraps(func)
        def inner(*args, **kwargs):
            factory = create_func_list_factory(chain_function, func)
            kwargs['func_list_factory'] = factory
            kwargs['func_list'] = factory()
            return exec_funcs(**kwargs)
        return inner
    return middle


class Menu:

    def __init__(self, options, title="", exit_text="", option_pattern=r'(?P<option>[\w]+)\_.*', prompt_string=""):
        self.title = title
        self.exit_text = exit_text
        self.prompt_string = prompt_string
        self.option_pattern = option_pattern
        self.options = OrderedDict(options)

    def print_menu(self):
        """returns the menu options string"""
        TITLE = self.title
        OPT_TEMP = "{}) {}\n"
        option_list = [OPT_TEMP.format(letter, option) for letter, option in option_titles(self.options)]
        return TITLE + "\n\n" + "".join(option_list)

    def prompt_text(self):
        """returns the prompt string with options range"""
        return self.prompt_string.format(option_list=", ".join([l for l, _ in self.options.items()]))

    def input_to_option(self, raw_option):
        """takes string input and returns corresponding index and func"""
        option = raw_option.strip().lower()[0]
        if option == "q":
            sys.exit(self.exit_text)
        if option not in self.options:
            raise ValueError()
        return self.options[option]

    def alert_display(self, alert):
        """returns alert message with newline, but only if alert exists"""
        return "::: {} :::\n".format(alert) if alert else ""

    def loop(self, callback):
        """runs the menu loop"""
        alert = None
        while True:
            clear()
            print(self.alert_display(alert))
            print(self.print_menu())
            print(self.prompt_text())
            alert = None
            raw_option = input(">>>  ")
            try:
                option = self.input_to_option(raw_option)
            except SystemExit as err:
                clear()
                raise err
            except:
                alert = "Bad input: please follow guidelines below"
                continue
            try:
                callback(option)
            except EndOption:
                pass
