import re
import sys
import os
from collections import OrderedDict
from functools import wraps, reduce

class EndOption(Exception):
    """Ends an option chain"""
    def __init__(self, message):
        self.message = message

def end(*args, **kwargs):
    raise EndOption("...   ")

def clear():
    """clears the screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def executor(*args, **kwargs):
    def inner(acc, cur):
        start_check = acc.__class__.__name__
        try:
            if start_check == 'function' or start_check == 'partial':
                acc = acc(*args, **kwargs)
            func = cur(**acc)
            return func
        except EndOption as err:
            input(err)
            raise 
    return inner

def exec_funcs(*args, **kwargs):
    funcs_arr = kwargs['func_list']
    return reduce(executor(*args, **kwargs), funcs_arr)

def list_print(*args, **kwargs):
    list_to_print = kwargs['list']
    title = kwargs['title']
    item = kwargs['item_template']
    if title:
        print(title)
    print("")
    for row in list_to_print:
        print(item.format(**row))
    print("___________________________________________________")
    print("")
    del kwargs['title']
    del kwargs['item_template']
    return kwargs

def multiline_input(*args, **kwargs):
    name = kwargs['name']
    prompt = kwargs['prompt']
    print(prompt)
    if "input" not in kwargs:
        kwargs['input'] = dict()
    kwargs['input'][name] = sys.stdin.read().strip()
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
    print("")
    confirmation = input_to_confirm and input('{} [Yn]  '.format(confirm_msg)).lower() != "n"
    kwargs['confirmation'] = confirmation
    return kwargs

def get_opt_name(option):
    """returns the truncated version of the option function
    
    >>> def add_entry():
    ...     pass
    ... 
    >>> get_opt_name(add_entry)
    'add'
    """
    return re.search(r'(?P<option>[\w]+)\_.*', option.__name__).group('option')

def choice_menu(*args, **kwargs):
    option_template = "{}) {}\n"
    title = kwargs['title']
    options = OrderedDict(kwargs['options'])
    name = kwargs['name']
    prompt = kwargs['prompt']
    option_names = [(l, get_opt_name(o)) for l, o in options.items()]
    option_list = map(
        lambda x: option_template.format(x[0], x[1]), 
        option_names
    )
    if 'alert' in kwargs:
        print(kwargs['alert'])
        print("")
        del kwargs['alert']
    print(title)
    print("")
    print("".join(option_list))
    del kwargs['title']
    kwargs = line_input(*args, **kwargs)
    option = kwargs['input'][name][0]
    if option == "q":
        sys.exit("GOODBYE")
    if option not in options.keys():
        kwargs['title'] = title
        kwargs['name'] = name
        kwargs['prompt'] = prompt
        kwargs['alert'] = "::: BAD INPUT  Please try again :::"
        clear()
        return choice_menu(**kwargs)
    choice_funcs = options[option]()
    func_list = kwargs['og_func_list'][:]
    wild_idx = func_list.index("*")
    func_list[wild_idx:wild_idx + 1] = choice_funcs
    kwargs['func_list'][:] = func_list
    return kwargs

def pause(*args, **kwargs):
    input("...   ")
    return kwargs

def clear_screen(*args, **kwargs):
    clear()
    return kwargs

def normalize_func_list(func_list, this):
    try:
        func_list[func_list.index("this")] = this
    except ValueError:
        pass
    return func_list

def option(**top_kwargs):
    """takes func_list and args"""
    def middle(func):
        @wraps(func)
        def inner(*args, **kwargs):
            kwargs['func_list'] = normalize_func_list(top_kwargs['func_list'][:], func)
            kwargs['og_func_list'] = kwargs['func_list'][:]
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
        option_list = [OPT_TEMP.format(letter, option) for letter, option in self.option_titles()]
        return TITLE + "\n\n" + "".join(option_list)

    def prompt_text(self):
        """returns the prompt string with options range"""
        return self.prompt_string.format(option_list=", ".join([l for l, _ in self.options.items()]))

    def option_titles(self):
        """returns a list of option names"""
        return [(l, get_opt_name(o)) for l, o in self.options.items()]

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
