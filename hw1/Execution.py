import CLI
import State

from abc import ABCMeta, abstractmethod

import subprocess
import io
import os
import re

class ExecutionError(Exception):
    pass

class Executable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self, input_bytes, state): raise NotImplementedError()

class EchoExecutable(Executable):

    def __init__(self, args):
        self.args = args

    def execute(self, input_bytes, state):
        return (' '.join(self.args) + '\n').encode('utf-8')

class PwdExecutable(Executable):
    
    def __init__(self, args):
        pass

    def execute(self, input_bytes, state):
        return (os.getcwd() + '\n').encode('utf-8')

class CatExecutable(Executable):
    
    def __init__(self, args):
        self.args = args

    def execute(self, input_bytes, state):
        if len(self.args) < 1:
            raise ExecutionError('use "man cat" to find out how this works')
        
        try:
            with open(self.args[0], 'rb') as file:
                content = file.read()
        except Exception as e:
            raise ExecutionError(e, "File not found")
        return content

class WcExecutable(Executable):
    
    def __init__(self, args):
        pass

    def execute(self, input_bytes, state):
        text = input_bytes.decode('utf-8')
        words = len(text.split())
        lines = len(text.split('\n'))
        bytes = len(input_bytes)

        return "{0} {1} {2}\n".format(lines, words, bytes).encode('utf-8')

class AssignExecutable(Executable):

    def __init__(self, args):
        self.name = args[0]
        self.value = args[1]

    def execute(self, input_bytes, state):
        state.set_variable_value(self.name, self.value)

        return b''

class ExitExecutable(Executable):

    def __init__(self, args):
        pass

    def execute(self, input_bytes, state):
        state.terminate()

        return b''


class CallExecutable(Executable):

    def __init__(self, args):
        self.args = args

    def execute(self, input_bytes, state):
        try:
            # raise NotImplementedError("External calls temporarily disabled")
            completed_subprocess = subprocess.run(args=self.args, input=input_bytes, stdout=subprocess.PIPE)
            return completed_subprocess.stdout
        except Exception as e:
            raise ExecutionError(e, "Error executing a command {0}".format(' '.join(self.args)))


class ExecutableCLIFactory():

    def create_executable(command):
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