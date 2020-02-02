import State
import Execution

import sys
import re
import argparse

class Command:

    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __str__(self):
        return "name={0}\nargs:\n{1}".format(self.name, self.args)

class CommandParser:

    def parse_command(text_command):
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

    def __init__(self, state):
        self.state = state
        self.pipe_splitter = WordSplitter(['|'], quoting_type='weak')

    def parse_line(self, line):
        text_commands = self.pipe_splitter.split_line(line)
        substitutor = ContextSubstitutor(self.state)
        commands = []
        for text_command in text_commands:
            expanded_text_command = substitutor.substitute(text_command)
            command = CommandParser.parse_command(expanded_text_command)
            commands.append(command)
            
        return commands


class UserInteraction:
        
    def loop(input_stream, output_stream):
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

    def __init__(self, split_by, quoting_type):
        self.split_by = split_by
        if quoting_type == 'weak':
            self.weak_quoting_type = True
        elif quoting_type == 'strong':
            self.weak_quoting_type = False
        else:
            raise ValueError()

    def split_line(self, line):
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

    def __init__(self, state):
        self.state = state

    def substitute(self, command):
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