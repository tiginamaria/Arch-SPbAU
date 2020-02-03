import CLI
import State

from abc import ABCMeta, abstractmethod

import subprocess
import io
import os
import re

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
        elif command.name == 'pwd':
            return PwdExecutable(command.args)
        elif command.name == 'exit':
            return ExitExecutable(command.args)
        elif command.name == 'cat':
            return CatExecutable(command.args)
        elif command.name == 'wc':
            return WcExecutable(command.args)
        else:
            return CallExecutable([command.name] + command.args)