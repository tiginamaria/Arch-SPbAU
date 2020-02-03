import unittest

import CLI
import State
import Execution

import os

# @unittest.SkipTest
class ExecutionTest(unittest.TestCase):

    def setUp(self):
        self.state = State.State()

    def test_echo_executable(self):
        command = CLI.Command("echo", ["arg1", "arg2"])
        executable = Execution.ExecutableCLIFactory.create_executable(command)

        self.assertIsInstance(executable, Execution.EchoExecutable)

        res = executable.execute(b"", self.state)
        self.assertEqual(b"arg1 arg2\n", res)

    def test_cat_executable_some_file(self):
        command = CLI.Command("cat", ["some_file"])
        executable = Execution.ExecutableCLIFactory.create_executable(command)

        self.assertIsInstance(executable, Execution.CatExecutable)

        res = executable.execute(b"", self.state)
        self.assertEqual(("some text" + os.linesep).encode('utf-8'), res)

    def test_cat_executable_empty_file(self):
        command = CLI.Command("cat", ["empty_file"])
        executable = Execution.ExecutableCLIFactory.create_executable(command)

        self.assertIsInstance(executable, Execution.CatExecutable)

        res = executable.execute(b"", self.state)
        self.assertEqual((os.linesep).encode('utf-8'), res)

    def test_cat_executable_no_file(self):
        command = CLI.Command("cat", ["no_file"])
        executable = Execution.ExecutableCLIFactory.create_executable(command)

        self.assertIsInstance(executable, Execution.CatExecutable)

        with self.assertRaises(Execution.ExecutionError):
            res = executable.execute(b"", self.state)


    def test_pwd_executable(self):
        command = CLI.Command("pwd", [])
        executable = Execution.ExecutableCLIFactory.create_executable(command)

        self.assertIsInstance(executable, Execution.PwdExecutable)

        res = executable.execute(b"", self.state)
        self.assertEqual((os.getcwd() + '\n').encode('utf-8'), res)

    def test_wc_executable(self):
        command = CLI.Command("wc", [])
        executable = Execution.ExecutableCLIFactory.create_executable(command)

        self.assertIsInstance(executable, Execution.WcExecutable)

        res = executable.execute(b"hello world", self.state)
        self.assertEqual(b"1 2 11\n", res)

        res = executable.execute(b"hello\n world", self.state)
        self.assertEqual(b"2 2 12\n", res)

        res = executable.execute(b"hello\n\n\n\nworld", self.state)
        self.assertEqual(b"5 2 14\n", res)

    def test_assign_executable(self):
        command = CLI.Command("a=hello world", [])
        executable = Execution.ExecutableCLIFactory.create_executable(command)

        self.assertIsInstance(executable, Execution.AssignExecutable)

        executable.execute(b"", self.state)
        self.assertEqual("hello world", self.state.get_variable_value("a"))

    def test_exit_executable(self):
        command = CLI.Command("exit", [])
        executable = Execution.ExecutableCLIFactory.create_executable(command)

        self.assertIsInstance(executable, Execution.ExitExecutable)

        self.assertEqual(False, self.state.is_program_terminated())
        executable.execute(b"", self.state)
        self.assertEqual(True, self.state.is_program_terminated())

    def test_call_executable_no_such_command(self):
        command = CLI.Command("no_file", [])
        executable = Execution.ExecutableCLIFactory.create_executable(command)

        self.assertIsInstance(executable, Execution.CallExecutable)

        with self.assertRaises(Execution.ExecutionError):
            executable.execute(b"", self.state)