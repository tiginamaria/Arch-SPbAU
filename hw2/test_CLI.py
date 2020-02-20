import unittest

import CLI
import State

# @unittest.SkipTest
class CommandParserTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_empty_command(self):
        res = CLI.CommandParser.parse_command("")

        self.assertEqual("true", res.name)
        self.assertEqual(0, len(res.args))

    def test_simple_command(self):
        res = CLI.CommandParser.parse_command("command arg1 arg2")

        self.assertEqual("command", res.name)
        self.assertEqual(2, len(res.args))
        self.assertEqual("arg1", res.args[0])
        self.assertEqual("arg2", res.args[1])

    def test_assign_command(self):
        res = CLI.CommandParser.parse_command("greetings=\"hello world\"")

        self.assertEqual("greetings=hello world", res.name)
        self.assertEqual(0, len(res.args))

    def test_remove_close_quotation(self):
        res = CLI.CommandParser.parse_command("echo '$[var'\" name]\"")

        self.assertEqual("echo", res.name)
        self.assertEqual(1, len(res.args))
        self.assertEqual("$[var name]", res.args[0])


# @unittest.SkipTest
class ContextSubstitutorTest(unittest.TestCase):

    def setUp(self):
        self.state = State.State()

    def test_no_substitution(self):
        substitutor = CLI.ContextSubstitutor(self.state)
        res = substitutor.substitute("echo hello")
        self.assertEqual("echo hello", res)

    def test_empty_substitution(self):
        substitutor = CLI.ContextSubstitutor(self.state)
        res = substitutor.substitute("echo $hello")
        self.assertEqual("echo ", res)

    def test_single_substitution(self):
        self.state.set_variable_value("hello", "bye")
        substitutor = CLI.ContextSubstitutor(self.state)
        res = substitutor.substitute("echo $hello")
        self.assertEqual("echo bye", res)

    def test_no_substitution_quoted(self):
        self.state.set_variable_value("hello", "bye")
        substitutor = CLI.ContextSubstitutor(self.state)
        res = substitutor.substitute("echo '$hello'")
        self.assertEqual("echo '$hello'", res)

    def test_substitution_despite_quoted(self):
        self.state.set_variable_value("hello", "bye")
        substitutor = CLI.ContextSubstitutor(self.state)
        res = substitutor.substitute("echo \"$hello\"")
        self.assertEqual("echo \"bye\"", res)

    def test_two_close_substitution(self):
        self.state.set_variable_value("hello", "bye")
        self.state.set_variable_value("world", " heaven")
        substitutor = CLI.ContextSubstitutor(self.state)
        res = substitutor.substitute("echo $hello$world")
        self.assertEqual("echo bye heaven", res)

# @unittest.SkipTest
class WordSplitterTest(unittest.TestCase):

    def setUp(self):
        self.splitter = CLI.WordSplitter(['|'], 'weak')

    def test_single_pipe(self):
        res = self.splitter.split_line("hello | world")
        self.assertEqual(["hello ", " world"], res)

    def test_multi_pipe(self):
        res = self.splitter.split_line("hello | world | again")
        self.assertEqual(["hello ", " world ", " again"], res)

    def test_quoted_pipe(self):
        res = self.splitter.split_line("hello '|' world")
        self.assertEqual(["hello '|' world"], res)

    def test_weakly_quoted_pipe(self):
        res = self.splitter.split_line("hello \"|\" world")
        self.assertEqual(["hello \"|\" world"], res)


# @unittest.SkipTest
class LineParserTest(unittest.TestCase):

    def setUp(self):
        self.state = State.State()

    def test_no_args(self):
        line_parser = CLI.LineParser(self.state)
        commands = line_parser.parse_line("command")
        self.assertEqual(1, len(commands))
        self.assertEqual("command", commands[0].name)
        self.assertEqual(0, len(commands[0].args))

    def test_no_args_piped(self):
        line_parser = CLI.LineParser(self.state)
        commands = line_parser.parse_line("command | other_one")
        self.assertEqual(2, len(commands))
        self.assertEqual("command", commands[0].name)
        self.assertEqual(0, len(commands[0].args))
        self.assertEqual("other_one", commands[1].name)
        self.assertEqual(0, len(commands[1].args))

    def test_complex_case(self):
        line_parser = CLI.LineParser(self.state)
        commands = line_parser.parse_line("echo kek | a=4 | pwd | wc | grep -iA hello | cd | ls /home")
        self.assertEqual(7, len(commands))

        self.assertEqual("echo", commands[0].name)
        self.assertEqual(1, len(commands[0].args))
        self.assertEqual("kek", commands[0].args[0])

        self.assertEqual("a=4", commands[1].name)
        self.assertEqual(0, len(commands[1].args))
        self.assertEqual("pwd", commands[2].name)
        self.assertEqual(0, len(commands[2].args))
        self.assertEqual("wc", commands[3].name)
        self.assertEqual(0, len(commands[3].args))

        self.assertEqual("grep", commands[4].name)
        self.assertEqual(2, len(commands[4].args))
        self.assertEqual("-iA", commands[4].args[0])
        self.assertEqual("hello", commands[4].args[1])

        self.assertEqual("cd", commands[5].name)
        self.assertEqual(0, len(commands[5].args))

        self.assertEqual("ls", commands[6].name)
        self.assertEqual(1, len(commands[6].args))
        self.assertEqual("/home", commands[6].args[0])
