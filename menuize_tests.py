from unittest import TestCase, main, mock
from collections import OrderedDict

import menuize


class MeunizeTests(TestCase):
    menu = None
    options = None

    config = {
        "title": "The title",
        "exit_text": "Goodbye",
        "prompt_string": "Enter choice\n({option_list})"
    }

    def setUp(self):
        def add_task(*args, **kwargs):
            pass
        def search_tasks(*args, **kwargs):
            pass
        def edit_task(*args, **kwargs):
            pass
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
        titles = self.menu.option_titles()
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



if __name__ == "__main__":
    main()