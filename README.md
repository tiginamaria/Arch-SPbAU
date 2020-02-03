# Arch-SPbAU

## Homework 1. My Bash (mash):

The application consists of 3 big modules: CLI, State, and Execution. Here the details about each module.

CLI: The module's main goal is to present to a user command-line interface. So it has classes to parse user's input and transform it to form (command_name, command_args[]) which is represented by the Command class.

State: The module's main goal it to implement internal state of the shell. Now it has support for envromental variables (with high usage of OS's help) and whether or not shell was terminated (presumably by execution of EXIT command).

Execution: The module's main goal is to execute Executables prepared for it by another modules. In our case ExecutableCLIFactory transforms CLI.Command into Executables that is performing connection between text command and real executables.

![Mash diagram](https://github.com/ivankrut856/Arch-SPbAU/blob/hw1/hw1/MashDiagram.png)
