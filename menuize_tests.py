import sys
from io import StringIO
from unittest import TestCase, main, mock
from collections import OrderedDict

import menuize

def add_task(*args, **kwargs):
    pass
def search_tasks(*args, **kwargs):
    pass
def edit_task(*args, **kwargs):
    pass


class MeunizeTests(TestCase):
    menu = None
    options = None

    config = {
        "title": "The title",
        "exit_text": "Goodbye",
        "prompt_string": "Enter choice\n({option_list})"
    }

    def setUp(self):
        self.options = [
            ('a', add_task),
            ('s', search_tasks),
            ('e', edit_task)
        ]
        self.menu = menuize.Menu(
            options=self.options,
            **self.config
        )

    def tearDown(self):
        self.menu = None
        self.options = None

    def test_init(self):
        for key, value in self.config.items():
            self.assertEqual(getattr(self.menu, key), value)

    def test_init_options(self):
        self.assertIsInstance(self.menu.options, OrderedDict)
        self.assertListEqual(
            [(key, value) for key, value in self.menu.options.items()], 
            self.options
        )

    def test_option_titles(self):
        titles = menuize.option_titles(self.menu.options)
        self.assertIsInstance(titles, list)
        self.assertListEqual(
            titles, 
            [('a', 'add'), ('s', 'search'), ('e', 'edit')]
        )

    def test_print_menu(self):
        menu_text = self.menu.print_menu()
        self.assertEqual(
            menu_text, 
            "The title\n\na) add\ns) search\ne) edit\n"
        )

    def test_prompt_text(self):
        prompt = self.menu.prompt_text()
        self.assertEqual(prompt, "Enter choice\n(a, s, e)")

    def test_input_to_option_returns_correct_option(self):
        option = self.menu.input_to_option("search")
        self.assertTrue(callable(option))
        self.assertEqual(option.__name__, "search_tasks")
    
    def test_input_to_option_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.menu.input_to_option("wrong")

    def test_input_to_option_raises_system_exit(self):
        with self.assertRaises(SystemExit):
            self.menu.input_to_option("quit")

    def test_alert_display(self):
        alert = self.menu.alert_display("BAD INPUT")
        self.assertEqual("::: BAD INPUT :::\n", alert)

    def test_end(self):
        with self.assertRaises(menuize.EndOption):
            menuize.end()

    def test_get_opt_name(self):
        def add_some_whatever():
            pass
        self.assertEqual(
            menuize.get_opt_name(add_some_whatever), 
            "add_some"
        )

    def test_normalize_func_list(self):
        def this():
            pass
        def chain_function():
            return [add_task, search_tasks, "this", "*", edit_task]
        self.assertListEqual(
            menuize.normalize_func_list(chain_function, this),
            [add_task, search_tasks, this, "*", edit_task]
        )

    def test_create_func_list_factory(self):
        def this():
            pass
        def chain_function():
            return [add_task, search_tasks, "this", "*", edit_task]
        factory = menuize.create_func_list_factory(
            chain_function=chain_function, 
            this=this
        )
        self.assertListEqual(
            factory(),
            [add_task, search_tasks, this, "*", edit_task]
        )
        # try it again
        self.assertListEqual(
            factory(),
            [add_task, search_tasks, this, "*", edit_task]
        )

    def test_executor_runs_second_function_first_with_arguments(self):
        fake_args = {"fake": "fake", "args":"args"}
        mocks = [
            mock.Mock(side_effect=lambda **x: x), 
            mock.Mock(side_effect=lambda **x: x), 
        ]
        inner = menuize.executor(**fake_args)
        result = inner(mocks[0], mocks[1])
        for mock_func in mocks:
            mock_func.assert_called_once_with(**fake_args)
        self.assertDictEqual(fake_args, result)

    def test_executor_runs_second_function_with_acc_result(self):
        fake_args = {"fake": "fake", "args":"args"}
        fake_args_from_acc = {"fake": "fake", "args":"args", "acc":"acc"}
        mock_func = mock.Mock(side_effect=lambda **x: x)
        inner = menuize.executor(**fake_args)
        result = inner(fake_args_from_acc, mock_func)
        mock_func.assert_called_once_with(**fake_args_from_acc)
        self.assertDictEqual(fake_args_from_acc, result)

    def test_executor_ends_properly(self):
        fake_args = {"fake": "fake", "args":"args"}
        fake_args_from_acc = {"fake": "fake", "args":"args", "acc":"acc"}
        inner = menuize.executor(**fake_args)
        with self.assertRaises(menuize.EndOption):
            result = inner(fake_args_from_acc, menuize.end)

    def test_exec_funcs(self):
        mocks = [
            mock.Mock(side_effect=lambda **x: x),
            mock.Mock(side_effect=lambda **x: x),
            mock.Mock(side_effect=lambda **x: x),
        ]
        fake_args = {"func_list": mocks}
        result = menuize.exec_funcs(**fake_args)
        for mock_func in mocks:
            mock_func.assert_called_once_with(**fake_args)
        self.assertDictEqual(result, fake_args)

    def test_list_string_with_title(self):
        kwargs = {
            "title": "Mock title",
            "item_template": "{name}",
            "list": [
                {"name": "nic"},
                {"name": "tonia"},
                {"name": "jack"},
            ]
        }
        string = menuize.list_string(**kwargs)
        self.assertEqual(string, "Mock title\n\n\nnic\ntonia\njack\n___________________________________________________\n")

    def test_list_string_without_title(self):
        kwargs = {
            "item_template": "{name}",
            "list": [
                {"name": "nic"},
                {"name": "tonia"},
                {"name": "jack"},
            ]
        }
        string = menuize.list_string(**kwargs)
        self.assertEqual(string, "\nnic\ntonia\njack\n___________________________________________________\n")

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_list_print(self, mock_stdout):
        kwargs = {
            "title": "Mock title",
            "item_template": "{name}",
            "list": [
                {"name": "nic"},
                {"name": "tonia"},
                {"name": "jack"},
            ]
        }
        kwargs = menuize.list_print(**kwargs)
        self.assertDictEqual(kwargs, {
            "list": [
                {"name": "nic"},
                {"name": "tonia"},
                {"name": "jack"},
            ]
        })
        self.assertEqual(
            mock_stdout.getvalue(),
            "Mock title\n\n\nnic\ntonia\njack\n___________________________________________________\n\n"
        )

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_multiline_input(self, mock_stdout):
        kwargs = {
            "name": "input_key",
            "prompt": "gimme input dude",
        }
        with mock.patch('sys.stdin', StringIO("  stUfF  ")): #mock_stdin):
            kwargs = menuize.multiline_input(**kwargs)
            self.assertEqual(
                mock_stdout.getvalue(),
                "gimme input dude\n\n"
            )
        self.assertEqual(kwargs['input']['input_key'], "stuff")
        self.assertNotIn('name', kwargs)
        self.assertNotIn('prompt', kwargs)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_line_input(self, mock_stdout):
        kwargs = {
            "name": "input_key",
            "prompt": "gimme input dude",
        }
        with mock.patch('sys.stdin', StringIO("  stUfF  ")):
            kwargs = menuize.line_input(**kwargs)
            self.assertEqual(
                mock_stdout.getvalue(),
                "gimme input dude >>>  "
            )
        self.assertEqual(kwargs['input']['input_key'], "stuff")
        self.assertNotIn('name', kwargs)
        self.assertNotIn('prompt', kwargs)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_numerical_input_returns_int(self, mock_stdout):
        kwargs = {
            "name": "input_key",
            "prompt": "gimme number input dude",
        }
        with mock.patch('sys.stdin', StringIO("  67  ")):
            kwargs = menuize.numerical_input(**kwargs)
            self.assertEqual(
                mock_stdout.getvalue(),
                "gimme number input dude >>>  "
            )
        self.assertEqual(kwargs['input']['input_key'], 67)
        self.assertNotIn('name', kwargs)
        self.assertNotIn('prompt', kwargs)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_numerical_input_raises_err(self, mock_stdout):
        kwargs = {
            "name": "input_key",
            "prompt": "gimme number input dude",
        }
        with mock.patch('sys.stdin', StringIO("  words  ")):
            with self.assertRaises(ValueError):
                kwargs = menuize.numerical_input(**kwargs)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_numerical_input_raises_err(self, mock_stdout):
        kwargs = {
            "name": "input_key",
            "prompt": "gimme number input dude",
        }
        with mock.patch('sys.stdin', StringIO("  words  ")):
            with self.assertRaises(ValueError):
                kwargs = menuize.numerical_input(**kwargs)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_confirmed_on_anything_but_n(self, mock_stdout):
        kwargs = {
            "confirm_msg": "ya sure dude?",
            "input": { "not": "empty"},
        }
        with mock.patch('sys.stdin', StringIO("  bes  ")):
            kwargs = menuize.confirmed(**kwargs)
            self.assertEqual(
                mock_stdout.getvalue(),
                "\nya sure dude? [Yn]  "
            )
        self.assertEqual(kwargs['confirmation'], True)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_confirmed_on_no(self, mock_stdout):
        kwargs = {
            "confirm_msg": "ya sure dude?",
            "input": { "not": "empty"},
        }
        with mock.patch('sys.stdin', StringIO("  n  ")):
            kwargs = menuize.confirmed(**kwargs)
            self.assertEqual(
                mock_stdout.getvalue(),
                "\nya sure dude? [Yn]  "
            )
        self.assertEqual(kwargs['confirmation'], False)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_confirmed_on_no_input(self, mock_stdout):
        kwargs = {
            "confirm_msg": "ya sure dude?",
            "input": dict(),
        }
        with mock.patch('sys.stdin', StringIO("y")):
            kwargs = menuize.confirmed(**kwargs)
        self.assertEqual(kwargs['confirmation'], False)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_print_choice_menu(self, mock_stdout):
        kwargs = {
            "title": "this title",
            "option_list": [("a", "add"), ("s","search"), ("e", "edit")],
        }
        kwargs = menuize.print_choice_menu(**kwargs)
        self.assertEqual(
            mock_stdout.getvalue(),
            "this title\n\na) add\ns) search\ne) edit\n\n___________________________________________________\n\n"
        )
        self.assertNotIn('title', kwargs)
        self.assertNotIn('item_template', kwargs)
        self.assertNotIn('list', kwargs)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_print_alert_with_alert(self, mock_stdout):
        kwargs = {
            "alert": "this alert",
        }
        kwargs = menuize.print_alert(**kwargs)
        self.assertEqual(
            mock_stdout.getvalue(),
            "::: this alert :::\n"
        )
        self.assertNotIn('alert', kwargs)

    def test_merge_option_branch(self):
        def this():
            pass
        def that():
            pass
        def other():
            pass
        def chain_function():
            return [add_task, search_tasks, "this", "*", edit_task]
        kwargs = {
            'func_list_factory': menuize.create_func_list_factory(
                    chain_function=chain_function, 
                    this=this
                ),
            'func_list': [add_task, search_tasks, "this", "*", edit_task]
        }
        option_branch = [that, other]
        kwargs = menuize.merge_option_branch(option_branch, kwargs)
        self.assertListEqual(
            kwargs['func_list'],
            [add_task, search_tasks, this, that, other, edit_task]
        )


if __name__ == "__main__":
    main()