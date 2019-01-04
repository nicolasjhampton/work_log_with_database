from unittest import TestCase, main, mock
from collections import OrderedDict

import menuize


class MeunizeTests(TestCase):
  menu = None
  add_task = None
  search_tasks = None
  options = None

  config = {
    "title": "The title",
    "exit_text": "Goodbye",
    "prompt_string": "Enter choice"
  }

  

  def setUp(self):
    self.add_task = mock.Mock()
    self.search_tasks = mock.Mock()
    self.options = [
      ('a', self.add_task),
      ('s', self.search_tasks)
    ]

    self.menu = menuize.Menu(
      # title="The title",
      # exit_text="Goodbye",
      # prompt_string="Enter choice",
      options=self.options,
      **self.config
    )
  
  def tearDown(self):
    self.menu = None
    self.add_task = None
    self.search_tasks = None
    self.options = None
  
  def test_init(self):
    for key, value in self.config.items():
      self.assertEqual(getattr(self.menu, key), value)
  
  def test_init_options(self):
    self.assertIsInstance(self.menu.options, OrderedDict)
    self.assertListEqual(
      list([(key, value) for key, value in self.menu.options.items()]), 
      self.options
    )

if __name__ == "__main__":
    main()