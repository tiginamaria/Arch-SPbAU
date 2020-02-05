import State
import Execution

import sys
import re
import argparse

class Command:
    """ Represents a command parsed from text """

    def __init__(self, name, args):
        """ Constructs an object with just a name and args

        Parameters.
        name: str
            The name which is to be stored as name of the command
        args: str[]
            The arguments which are to be stored as arguments of the command

        """

        self.name = name
        self.args = args

    def __str__(self):
        return "name={0}\nargs:\n{1}".format(self.name, self.args)

class CommandParser:
    """ Represents a parser with the single method which parses a command from text """

    def parse_command(text_command):
        """ Parses a command from text

        Parameters.
        text_command: str
            The text from which a command is about to be parsed

        Returns.
        Command
            The command parsed from a text
        """

        result = []
        current = []
        is_strong_quoting_on = False
        is_weak_quoting_on = False
        for ch in text_command:
            if not is_strong_quoting_on and ch == '"':
                is_weak_quoting_on = not is_weak_quoting_on
                continue

            if not is_weak_quoting_on and ch == '\'':
                is_strong_quoting_on = not is_strong_quoting_on
                continue

            if not is_strong_quoting_on and not is_weak_quoting_on and ch in [' ', '\t', '\n', '\r']:
                if current:
                    result.append(''.join(current))
                    current = []
                continue

            current.append(ch)

        if len(current) > 0:
            result.append(''.join(current))
            current = []

        if not result:
            return Command('true', [])

        return Command(result[0], result[1:])


class LineParser:
    """ Represents a parser with the single method which parses a series of commands from the given line """

    def __init__(self, state):
        """ Construct an object with given state of the execution

        Parameters.
        state: State.State
            The state of the execution for which the parser should parse
        """

        self.state = state
        self.pipe_splitter = WordSplitter(['|'], quoting_type='weak')

    def parse_line(self, line):
        """ Parses commands from the given line

        Parameters.
        line: str
            The line from which commands are to be parsed
        """

        text_commands = self.pipe_splitter.split_line(line)
        substitutor = ContextSubstitutor(self.state)
        commands = []
        for text_command in text_commands:
            expanded_text_command = substitutor.substitute(text_command)
            command = CommandParser.parse_command(expanded_text_command)
            commands.append(command)
            
        return commands


class UserInteraction:
    """ Represent the main CLI worker of the application """
        
    def loop(input_stream, output_stream):
        """ Performs loop for interacting with the user

        Parameters.
        input_stream: TextIOBase
            The text input stream through which the user will send commands to the application
        output_stream: TextIOBase
            The text output stream through which the responses to the user's commands are to be delivered
        """

        state = State.State()

        while not state.is_program_terminated():
            output_stream.write("> ")
            output_stream.flush()

            line = input_stream.readline()

            if not line:
                exit(0)

            parser = LineParser(state)
            commands = parser.parse_line(line)
            executables = list(map(Execution.ExecutableCLIFactory.create_executable, commands))

            error = False
            last_result = "".encode('utf-8')
            for executable in executables:
                try:
                    last_result = executable.execute(last_result, state)
                except Execution.ExecutionError as e:
                    error = True
                    output_stream.write(str(e) + '\n')
                    output_stream.flush()
                    break
            if error:
                continue

            if state.is_program_terminated():
                break

            output_stream.write(last_result.decode('utf-8'))
            output_stream.flush()


class WordSplitter:
    """ Represents a part of the parsing complex -- word splitter (or tokenizer), which splits a line into tokens """

    def __init__(self, split_by, quoting_type):
        """ Construct an object of the splitter with given delimiters and quoting type

        Parameters.
        split_by: str
            The string containing all delimiters about which the splitter will care
        quoting_type: str
            Must be either 'weak' or 'strong'. 'Weak' means that both of quotationg will affect splitting weak and strong.
            'Strong', contratily, means that only strong quotation will affect splitting, weak one, at the same time, will be ignored.

        Raises.
        ValueError
            If the quoting_type given to this constructor is wrong
        """

        self.split_by = split_by
        if quoting_type == 'weak':
            self.weak_quoting_type = True
        elif quoting_type == 'strong':
            self.weak_quoting_type = False
        else:
            raise ValueError('Unsupported quoting type')

    def split_line(self, line):
        """ Splits the given line into several strings

        Parameters.
        line: str
            The line which is to be splitted

        Returns.
        str[]
            The list of strings got from the splitting process
        """

        is_strong_quoting_on = False
        is_weak_quoting_on = False

        result = []
        current = []
        for ch in line:
            if not is_weak_quoting_on and ch == '\'':
                is_strong_quoting_on = not is_strong_quoting_on

            if not is_strong_quoting_on and ch == '"':
                is_weak_quoting_on = not is_weak_quoting_on

            if not is_strong_quoting_on and (not self.weak_quoting_type or not is_weak_quoting_on) and ch in self.split_by:
                result.append(current)
                current = []
            else:
                current.append(ch)

        if len(current) > 0:
            result.append(current)

        for i in range(len(result)):
            result[i] = ''.join(result[i])

        return result


class ContextSubstitutor:
    """ Represents a part of the parsing complex -- context substitutor, which evaluates substitutions according to the given state """

    def __init__(self, state):
        """ Constructs an object with the given state

        Parameters.
        state: State.State
            The state of execution from which values of variables will be taken
        """

        self.state = state

    def substitute(self, command):
        """ Performs evaluation of substitutions in the given text of the command

        Parameters.
        command: str
            The text of the command inside which substitutions are to be evaluated

        Returns.
        str
            The modified text of the command with substitutions evaluated
        """
        
        is_strong_quoting_on = False

        i = 0
        while (i < len(command)):
            if command[i] == '\'':
                is_strong_quoting_on = not is_strong_quoting_on

            if not is_strong_quoting_on and command[i] == "$":
                result = re.match(r'[\w_]+', command[i + 1:])
                if result is not None:
                    variable_name = result.group(0)
                    end = result.end()
                    replace_by = self.state.get_variable_value(variable_name)
                    command = ''.join([command[:i], replace_by, command[i + 1 + end:]])

            i += 1

        return command