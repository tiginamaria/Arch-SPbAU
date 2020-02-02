import os

class State:

    def __init__(self):
        self.terminated = False

    def get_variable_value(self, variable_name):
        return os.getenv(variable_name, "")

    def set_variable_value(self, variable_name, value):
        os.environ[variable_name] = value

    def terminate(self):
        self.terminated = True

    def is_program_terminated(self):
        return self.terminated
