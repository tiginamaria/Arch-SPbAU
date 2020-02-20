from pathlib import Path

import CLI
import State

from abc import ABCMeta, abstractmethod

import subprocess
import io
import os
import re
from functools import reduce
import click

class ExecutionError(Exception):
    """ The base exception class to represent any errors happening during execution """

    pass

class Executable:
    """ Abstract base class for type that are to be executed in given way """

    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self, input_bytes, state):
        """ Base method for executing executables 
        
        Parameters.
        input_bytes: bytes
            Input byte sequence given as stdin to the command
        state: State.State
            Initial execution state

        Returns.
        bytes
            Output byte sequence of command.
        """

        raise NotImplementedError()

class GrepExecutable(Executable):
    """ Represents executable for an GREP command which parse files and finds patterns """

    @click.command(name="grep", add_help_option=False)
    @click.option('-i', 'case_insensitive', is_flag=True)
    @click.option('-w', 'only_whole_words', is_flag=True)
    @click.option('-A', 'lines_after', default=0, type=int)
    @click.argument("regex")
    @click.argument("files", nargs=-1)
    @click.pass_obj
    def parser(self, case_insensitive, only_whole_words, lines_after, regex, files):
        """ Callback for a click.Command for parsing arguments for the command. Put them into callee object

        Parameters.
        case_insensitive: boolean
            Whether or not the search must respect symbols case
        only_whole_words: boolean
            Whether or not the search must find only whole world matching pattern
        lines_after: boolean
            How many line (except matched) will be printed after the match (default: 0)
        regex: string
            The regular expression which represents the pattern to search
        files: string[]
            The files in which the search will be performed. If empty then from input byte sequence

        """
        self.case_insensitive = case_insensitive
        self.only_whole_words = only_whole_words
        self.lines_after = lines_after
        self.regex = regex
        self.files = files

    def __init__(self, args):
        """ Constructs a command object with given arguments """

        try:
            ctx = GrepExecutable.parser.make_context("grep", args, obj=self)
        except (click.ClickException, click.Abort) as e:
            self.parsing_exception = e
            return

        with ctx:
            GrepExecutable.parser.invoke(ctx)

        self.parsing_exception = None

    def execute(self, input_bytes, state):
        """ Executing executable
        
        Parameters.
        input_bytes: bytes
            Input byte sequence given as stdin to the command
        state: State.State
            Initial execution state

        Returns.
        bytes
            Output byte sequence of command.
        """

        if self.parsing_exception is not None:
            raise ExecutionError(self.parsing_exception)

        if not self.files:
            text = input_bytes.decode('utf-8').split('\n')
            searchables = [(text, '<stdin>')]
        else:
            def file_to_searchable(filename):
                with open(filename, "r") as file:
                    text = file.readlines()
                    return (text, filename)

            try:
                searchables = list(map(file_to_searchable, self.files))
            except Exception as e:
                raise ExecutionError(e)

        res = []
        for (text, filename) in searchables:
            res.append("{0}:\n".format(filename))
            res.extend(self.process_lines(text))

        return ''.join(res).encode('utf-8')

    def process_lines(self, lines):
        """ Process lines and return formatted matched lines and other context

        Parameters.
        lines: string[]

        Returns.
        Blocks of lines separated by '--' where each block contains one or several matched lines and given number of lines after a match

        """
        regex = self.regex
        if self.only_whole_words:
            regex = r"\b" + regex + r"\b"
        compiled = re.compile(regex, (self.case_insensitive * re.I))

        intervals_containing_match = []
        for i in range(len(lines)):
            if compiled.search(lines[i]):
                intervals_containing_match.append((i, i + 1 + self.lines_after))

        merged_intervals = []
        current_r = None
        current_l = None
        for (l, r) in intervals_containing_match:
            if current_r is None:
                (current_l, current_r) = (l, r)
                continue

            if current_r >= l:
                current_r = r
            else:
                merged_intervals.append((current_l, current_r))
                (current_l, current_r) = (l, r)

        if current_r is not None:
            merged_intervals.append((current_l, current_r))

        merged_matches = list(map(lambda interval: '\n'.join(lines[interval[0]:interval[1]]), merged_intervals))
        merged_text = [el for match in merged_matches for el in ['--\n', match, '\n']]

        return merged_text


class EchoExecutable(Executable):
    """ Represents executable for an ECHO command which prints its arguments """

    def __init__(self, args):
        """ Constructs a command object with given arguments """

        self.args = args

    def execute(self, input_bytes, state):
        """ Executing executable
        
        Parameters.
        input_bytes: bytes
            Input byte sequence given as stdin to the command
        state: State.State
            Initial execution state

        Returns.
        bytes
            Output byte sequence of command.
        """

        return (' '.join(self.args) + '\n').encode('utf-8')

class PwdExecutable(Executable):
    """ Represents executable for an PWD command which prints current working directory """
    
    def __init__(self, args):
        pass

    def execute(self, input_bytes, state):
        """ Executing executable
        
        Parameters.
        input_bytes: bytes
            Input byte sequence given as stdin to the command
        state: State.State
            Initial execution state

        Returns.
        bytes
            Output byte sequence of command.
        """

        return (os.getcwd() + '\n').encode('utf-8')

class CatExecutable(Executable):
    """ Represents executable for an CAT command which prints file given through first argument """

    def __init__(self, args):
        """ Constructs a command object with given arguments 

        Contract.
        The length of args list must be 1 or execute() will throw an ExecutionError exception
        """

        self.args = args

    def execute(self, input_bytes, state):
        """ Executing executable
        
        Parameters.
        input_bytes: bytes
            Input byte sequence given as stdin to the command
        state: State.State
            Initial execution state

        Returns.
        bytes
            Output byte sequence of command.

        Throws.
        ExecutionError
            If the length of args list doesn't equal 1
        ExecutionError
            If no file from first argument found
        """

        if len(self.args) < 1:
            raise ExecutionError('use "man cat" to find out how this works')

        try:
            with open(self.args[0], 'rb') as file:
                content = file.read()
        except Exception as e:
            raise ExecutionError(e, "File not found")
        return content

class WcExecutable(Executable):
    """ Represents executable for an WC command which prints number of lines, words and bytes in the given input bytes """
    
    def __init__(self, args):
        pass

    def execute(self, input_bytes, state):
        """ Executing executable
        
        Parameters.
        input_bytes: bytes
            Input byte sequence given as stdin to the command
        state: State.State
            Initial execution state

        Returns.
        bytes
            Output byte sequence of command.
        """

        text = input_bytes.decode('utf-8')
        words = len(text.split())
        lines = len(text.split('\n'))
        bytes = len(input_bytes)

        return "{0} {1} {2}\n".format(lines, words, bytes).encode('utf-8')


class CdExecutable(Executable):
    """ Represents executable for an CD command which change the shell working directory """

    def __init__(self, args):
        self.args = args

    def execute(self, input_bytes, state):
        """ Executing executable

        Parameters.
        input_bytes: bytes
            Input byte sequence given as stdin to the command
        state: State.State
            Initial execution state

        Returns.
        bytes
            Output byte sequence of command.
        """

        if len(self.args) > 1:
            raise ExecutionError('Error executing a command cd. Expected 0-1 arguments, got {}:{}'
                                 .format(len(self.args), self.args))
        try:
            directory = os.path.expanduser(self.args[0]) if len(self.args) == 1 else str(Path.home())
            os.chdir(directory)
        except FileNotFoundError:
            raise ExecutionError('Error executing a command cd. No such directory: {}'.format(self.args[0]))
        except NotADirectoryError:
            raise ExecutionError('Error executing a command cd. Not a directory: {}'.format(self.args[0]))
        except OSError:
            raise ExecutionError('Error executing a command cd. Can not list directory: {}'.format(self.args[0]))

        return b''


class LsExecutable(Executable):
    """ Represents executable for an LS command which list directory contents """

    def __init__(self, args):
        self.args = args

    def execute(self, input_bytes, state):
        """ Executing executable

        Parameters.
        input_bytes: bytes
            Input byte sequence given as stdin to the command
        state: State.State
            Initial execution state

        Returns.
        bytes
            Output byte sequence of command.
        """

        if len(self.args) > 1:
            raise ExecutionError('Error executing a command ls. Expected 0-1 arguments, got {}:{}'
                                 .format(len(self.args), self.args))
        directory = self.args[0] if len(self.args) == 1 else '.'
        try:
            content = os.listdir(directory)
        except FileNotFoundError:
            raise ExecutionError('Error executing a command ls. No such directory: {}'.format(directory))
        except NotADirectoryError:
            raise ExecutionError('Error executing a command ls. Not a directory: {}'.format(directory))
        except OSError:
            raise ExecutionError('Error executing a command ls. Can not list directory: {}'.format(directory))
        return ('\n'.join(content) + '\n').encode('utf-8')


class AssignExecutable(Executable):
    """ Represents assignment expression var_name=var_value, changes the OS's environment correspondingly """

    def __init__(self, args):
        """ Construct an object from to args where the first is a var_name and the second is a var_value.

        Contract.
        The length of args list must be 2. If more the rest will be ignored, if less an error will be produced
        """

        self.name = args[0]
        self.value = args[1]

    def execute(self, input_bytes, state):
        """ Executing executable
        
        Parameters.
        input_bytes: bytes
            Input byte sequence given as stdin to the command
        state: State.State
            Initial execution state

        Returns.
        bytes
            Output byte sequence of command.
        """
        
        state.set_variable_value(self.name, self.value)

        return b''

class ExitExecutable(Executable):
    """ Represent executable for an EXIT command which terminates the shell """

    def __init__(self, args):
        pass

    def execute(self, input_bytes, state):
        """ Executing executable

        Parameters.
        input_bytes: bytes
            Input byte sequence given as stdin to the command
        state: State.State
            Initial execution state

        Returns.
        bytes
            Output byte sequence of command.
        """

        state.terminate()

        return b''


class CallExecutable(Executable):
    """ Represents executable for an external program call """

    def __init__(self, args):
        self.args = args

    def execute(self, input_bytes, state):
        """ Executing executable
        
        Parameters.
        input_bytes: bytes
            Input byte sequence given as stdin to the command
        state: State.State
            Initial execution state

        Returns.
        bytes
            Output byte sequence of command.

        Throws.
        Execution error
            If no such external command exists
        Execution error
            If there was an error during external call
        """

        try:
            # raise NotImplementedError("External calls temporarily disabled")
            completed_subprocess = subprocess.run(args=self.args, input=input_bytes, stdout=subprocess.PIPE)
            return completed_subprocess.stdout
        except Exception as e:
            raise ExecutionError(e, "Error executing a command {0}".format(' '.join(self.args)))


class ExecutableCLIFactory():
    """ A factory preparing CLI.Commands for an execution """

    def create_executable(command):
        """ Dispatches between supporting command and returns an executable """
        
        matched = re.match(r'^([\w_]+)=(.*)$', command.name)

        if matched is not None:
            return AssignExecutable([matched.group(1), matched.group(2)])
        elif command.name == 'echo':
            return EchoExecutable(command.args)
        elif command.name == 'grep':
            return GrepExecutable(command.args)
        elif command.name == 'pwd':
            return PwdExecutable(command.args)
        elif command.name == 'exit':
            return ExitExecutable(command.args)
        elif command.name == 'cat':
            return CatExecutable(command.args)
        elif command.name == 'wc':
            return WcExecutable(command.args)
        elif command.name == 'cd':
            return CdExecutable(command.args)
        elif command.name == 'ls':
            return LsExecutable(command.args)
        else:
            return CallExecutable([command.name] + command.args)