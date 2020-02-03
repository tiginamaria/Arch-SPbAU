import os

class State:
    """ The class storing a state of execution, epsecially environmental variables and whether the shell was terminated or not """

    def __init__(self):
        """ Constructs an object with terminated=False by defauls """

        self.terminated = False

    def get_variable_value(self, variable_name):
        """ Returns a value of a variable

        Parameters.
        variable_name: str
            The name of the variable, the value of which is to be returned

        Returns.
        str
            The value of the variable
        """

        return os.getenv(variable_name, "")

    def set_variable_value(self, variable_name, value):
        """ Sets a value of a variable

        Parameters.
        variable_name: str
            The name of the variabe, the value of which is to be set
        value:
            The value to be set for the variable
        """

        os.environ[variable_name] = value

    def terminate(self):
        """ Mark the program as terminated """

        self.terminated = True

    def is_program_terminated(self):
        """ Checks whether or not the program was marked as terminated """

        return self.terminated
