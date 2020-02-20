import unittest
from pathlib import Path

import CLI
import State
import Execution

import os

# @unittest.SkipTest
class ExecutionTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.project_dir = os.getcwd()

    def setUp(self):
        self.state = State.State()
        os.chdir(self.project_dir)

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
        self.assertEqual(("some text\n").encode('utf-8'), res)

    def test_cat_executable_empty_file(self):
        command = CLI.Command("cat", ["empty_file"])
        executable = Execution.ExecutableCLIFactory.create_executable(command)

        self.assertIsInstance(executable, Execution.CatExecutable)

        res = executable.execute(b"", self.state)
        self.assertEqual(("\n").encode('utf-8'), res)

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

    def test_cd_executable_no_args(self):
        command = CLI.Command("cd", [])
        executable = Execution.ExecutableCLIFactory.create_executable(command)

        self.assertIsInstance(executable, Execution.CdExecutable)

        res = executable.execute(b"", self.state)
        self.assertEqual(b"", res)
        self.assertEqual(str(Path.home()), os.getcwd())

    def test_cd_executable(self):
        arg = "resources" + os.path.sep + "directory1"
        command = CLI.Command("cd", [arg])
        executable = Execution.ExecutableCLIFactory.create_executable(command)
        self.assertIsInstance(executable, Execution.CdExecutable)

        expected_dir = os.path.join(os.path.sep, os.getcwd(), arg)
        executable.execute(b"", self.state)
        self.assertEqual(expected_dir, os.getcwd())

    def test_cd_executable_arg_back(self):
        dir1, dir2 = "resources", "directory1"
        arg = dir1 + os.path.sep + dir2
        command = CLI.Command("cd", [arg])
        executable = Execution.ExecutableCLIFactory.create_executable(command)
        self.assertIsInstance(executable, Execution.CdExecutable)

        root_dir = os.getcwd()
        expected_dir = os.path.join(os.path.sep, root_dir, arg)
        executable.execute(b"", self.state)
        self.assertEqual(expected_dir, os.getcwd())

        arg = ".."
        command = CLI.Command("cd", [arg])
        executable = Execution.ExecutableCLIFactory.create_executable(command)
        self.assertIsInstance(executable, Execution.CdExecutable)

        expected_dir = os.path.join(os.path.sep, root_dir, dir1)
        executable.execute(b"", self.state)
        self.assertEqual(expected_dir, os.getcwd())

    def test_cd_pwd_executable(self):
        arg = "resources" + os.path.sep + "directory1"
        command = CLI.Command("cd", [arg])
        executable_cd = Execution.ExecutableCLIFactory.create_executable(command)
        self.assertIsInstance(executable_cd, Execution.CdExecutable)

        command = CLI.Command("pwd", [])
        executable_pwd = Execution.ExecutableCLIFactory.create_executable(command)
        self.assertIsInstance(executable_pwd, Execution.PwdExecutable)

        expected_dir = os.path.join(os.path.sep, os.getcwd(), arg)
        executable_cd.execute(b"", self.state)
        dir = executable_pwd.execute(b"", self.state)
        self.assertEqual((expected_dir + '\n').encode('utf-8'), dir)

    def test_cd_executable_exceptions(self):
        arg = "no_such_directory"
        command = CLI.Command("cd", [arg])
        executable = Execution.ExecutableCLIFactory.create_executable(command)
        self.assertIsInstance(executable, Execution.CdExecutable)
        self.assertRaises(Execution.ExecutionError, executable.execute, b"", self.state)

        arg = "CLI.py"
        command = CLI.Command("cd", [arg])
        executable = Execution.ExecutableCLIFactory.create_executable(command)
        self.assertIsInstance(executable, Execution.CdExecutable)
        self.assertRaises(Execution.ExecutionError, executable.execute, b"", self.state)

    def test_ls_executable_no_args(self):
        arg = "resources"
        command = CLI.Command("cd", [arg])
        executable_cd = Execution.ExecutableCLIFactory.create_executable(command)
        self.assertIsInstance(executable_cd, Execution.CdExecutable)
        executable_cd.execute(b"", self.state)

        command = CLI.Command("ls", [])
        executable = Execution.ExecutableCLIFactory.create_executable(command)
        self.assertIsInstance(executable, Execution.LsExecutable)
        res = executable.execute(b"", self.state)
        self.assertEqual({"directory1", "file1"}, set(res.decode('utf-8').strip('\n').split('\n')))

    def test_ls_executable(self):
        arg = "resources"
        command = CLI.Command("ls", [arg])
        executable = Execution.ExecutableCLIFactory.create_executable(command)
        self.assertIsInstance(executable, Execution.LsExecutable)
        res = executable.execute(b"", self.state)
        self.assertEqual({"directory1", "file1"}, set(res.decode('utf-8').strip('\n').split('\n')))

        arg = "resources" + os.path.sep + "directory1"
        command = CLI.Command("ls", [arg])
        executable = Execution.ExecutableCLIFactory.create_executable(command)
        self.assertIsInstance(executable, Execution.LsExecutable)
        res = executable.execute(b"", self.state)
        self.assertEqual({"file2", "file3"}, set(res.decode('utf-8').strip('\n').split('\n')))

    def test_ls_executable_exceptions(self):
        arg = "no_such_directory"
        command = CLI.Command("ls", [arg])
        executable = Execution.ExecutableCLIFactory.create_executable(command)
        self.assertIsInstance(executable, Execution.LsExecutable)
        self.assertRaises(Execution.ExecutionError, executable.execute, b"", self.state)

        arg = "CLI.py"
        command = CLI.Command("ls", [arg])
        executable = Execution.ExecutableCLIFactory.create_executable(command)
        self.assertIsInstance(executable, Execution.LsExecutable)
        self.assertRaises(Execution.ExecutionError, executable.execute, b"", self.state)

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

# @unittest.SkipTest
class GrepTest(unittest.TestCase):

    def setUp(self):
        self.state = State.State()

    def test_simple_grep(self):
        command = CLI.Command("grep", ["patter"])
        executable = Execution.ExecutableCLIFactory.create_executable(command)

        self.assertIsInstance(executable, Execution.GrepExecutable)

        res = executable.execute(b"pattern", self.state)

        self.assertEqual(b"<stdin>:\n--\npattern\n", res)

    def test_case_insensetive_grep(self):
        command = CLI.Command("grep", ["-i", "patter"])
        executable = Execution.ExecutableCLIFactory.create_executable(command)

        self.assertIsInstance(executable, Execution.GrepExecutable)

        res = executable.execute(b"pAtTeRn", self.state)

        self.assertEqual(b"<stdin>:\n--\npAtTeRn\n", res)

    def test_only_whole_word(self):
        command = CLI.Command("grep", ["-w", "pat"])
        executable = Execution.ExecutableCLIFactory.create_executable(command)

        self.assertIsInstance(executable, Execution.GrepExecutable)

        res = executable.execute(b"pattern", self.state)

        self.assertEqual(b"<stdin>:\n", res)

    def test_lines_after_option(self):
        command = CLI.Command("grep", ["-A 2", "pat"])
        executable = Execution.ExecutableCLIFactory.create_executable(command)

        self.assertIsInstance(executable, Execution.GrepExecutable)

        res = executable.execute(b"pattern\nfirst\nsecond\nthird", self.state)

        self.assertEqual(b"<stdin>:\n--\npattern\nfirst\nsecond\n", res)

    def test_invalid_options(self):
        command = CLI.Command("grep", ["-b 2", "pat"])
        executable = Execution.ExecutableCLIFactory.create_executable(command)

        with self.assertRaises(Execution.ExecutionError):
            executable.execute(b"", self.state)