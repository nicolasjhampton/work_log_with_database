import re
import sys
import os
from functools import wraps, reduce

def clear():
    """clears the screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def executor(*args, **kwargs):
    def inner(acc, cur):
        start_check = acc.__class__.__name__
        if start_check == 'function' or start_check == 'partial':
            acc = acc(*args, **kwargs)
        return cur(**acc)
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
    print("----------------------------------------------")
    print("")
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

def option(func_list=None):
    """takes func_list and args"""
    def middle(func):
        @wraps(func)
        def inner(*args, **kwargs):
            kwargs['func_list'] = normalize_func_list(func_list, func)
            return exec_funcs(**kwargs)
        return inner
    return middle

class Init:

    def __init__(self, title="", exit_text="", option_pattern=r'(?P<option>[\w]+)\_.*', prompt_string="", **kwargs):
        self.title = title
        self.exit_text = exit_text
        self.prompt_string = prompt_string
        self.option_pattern = option_pattern
        self.options = kwargs['options']

    def print_menu(self):
        """returns the menu options string
        
        >>> print(print_menu([('a', 'add'), ('v', 'view'), ('d', 'delete')]))
        Welcome to your diary!
        <BLANKLINE>
        a) add
        v) view
        d) delete
        <BLANKLINE>
        """
        TITLE = self.title
        OPT_TEMP = "{}) {}\n"
        option_list = [OPT_TEMP.format(letter, option) for letter, option in self.option_titles()]
        return TITLE + "".join(option_list)

    def prompt_text(self):
        """returns the prompt string with options range
        
        >>> from collections import OrderedDict
        >>> options = OrderedDict([('a', 'add_entry'), ('v', 'view_entries'), ('d', 'delete_entry')])
        >>> print(prompt_text(options))
        What would you like to do?
        (Enter either a, v, d, or q to quit)
        <BLANKLINE>
        """
        return self.prompt_string.format(option_list=", ".join([l for l, _ in self.options.items()]))

    def get_opt_name(self, option):
        """returns the truncated version of the option function
        
        >>> def add_entry():
        ...     pass
        ... 
        >>> get_opt_name(add_entry)
        'add'
        """
        return re.search(self.option_pattern, option.__name__).group('option')

    def option_titles(self):
        """returns a list of option names
        
        >>> from collections import OrderedDict
        >>> def add_entry():
        ...     pass
        ... 
        >>> def delete_entry():
        ...     pass
        ... 
        >>> def view_entries():
        ...     pass
        ... 
        >>> options = OrderedDict([('a', add_entry), ('v', view_entries), ('d', delete_entry)])
        >>> option_titles(options)
        [('a', 'add'), ('v', 'view'), ('d', 'delete')]
        """
        return [(l, self.get_opt_name(o)) for l, o in self.options.items()]

    def input_to_option(self, raw_option):
        """takes numerical string input and returns corresponding index and func
        
        >>> from collections import OrderedDict
        >>> def add_entry():
        ...      pass
        ... 
        >>> def delete_entry():
        ...      pass
        ... 
        >>> def view_entries():
        ...      pass
        ...
        >>> options = OrderedDict([('a', add_entry), ('v', view_entries), ('d', delete_entry)])
        >>> input_to_option(" v ", options).__name__
        'view_entries'
        """
        option = raw_option.strip().lower()[0]
        if option == "q":
            sys.exit(self.exit_text)
        if option not in self.options:
            raise ValueError()
        return self.options[option]

    def alert_display(self, alert):
        """returns alert message with newline, but only if alert exists
        
        >>> alert_display("")
        ''
        >>> alert_display(None)
        ''
        >>> alert_display("Hello good lookin!")[:-2]
        'Hello good lookin'
        """
        return "{}\n".format(alert) if alert else ""

    def menu(self, callback):
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
                alert = "::: Bad input: please follow guidelines below :::"
                continue
            callback(option)