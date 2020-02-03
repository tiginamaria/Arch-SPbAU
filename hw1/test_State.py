import unittest

import State

# @unittest.SkipTest
class StateTest(unittest.TestCase):

    def setUp(self):
        self.state = State.State()

    def test_not_terminated_by_default(self):
        self.assertEqual(False, self.state.is_program_terminated())

    def test_set_get_the_same(self):
        self.state.set_variable_value("test_var", "test_val")
        self.assertEqual("test_val", self.state.get_variable_value("test_var"))
        self.state.set_variable_value("test_var", "")
        self.assertEqual("", self.state.get_variable_value("test_var"))

    def test_termination(self):
        self.state.terminate()
        self.assertEqual(True, self.state.is_program_terminated())