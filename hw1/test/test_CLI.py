import unittest
import CLI
import State

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
        commands = line_parser.parse_line("echo kek | a=4 | pwd | wc | grep -iA hello")
        self.assertEqual(5, len(commands))

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
