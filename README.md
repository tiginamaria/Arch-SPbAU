# Arch-SPbAU

## Homework 1. My Bash (mash):

The application consists of 3 big modules: CLI, State, and Execution. Here the details about each module.

CLI: The module's main goal is to present to a user command-line interface. So it has classes to parse user's input and transform it to form (command_name, command_args[]) which is represented by the Command class.

State: The module's main goal it to implement internal state of the shell. Now it has support for envromental variables (with high usage of OS's help) and whether or not shell was terminated (presumably by execution of EXIT command).

Execution: The module's main goal is to execute Executables prepared for it by another modules. In our case ExecutableCLIFactory transforms CLI.Command into Executables that is performing connection between text command and real executables.

![Mash diagram](https://github.com/ivankrut856/Arch-SPbAU/blob/hw1/hw1/MashDiagram.png)

## Homework 2. Parsing argument for grep. Analysis of alternative libraries for parsing.

There've been considered three quite popular options: argparse (default for python right now), optparse (was default) and click (optparse with RTX ON (meaning better version))

Argparse was my first choice, and I even wrote some lines of code with it. But soon I realised that it unconditionally exits after arguments parsing. One way to fix it is to catch SystemExit exception, but it's such a stupid way to build your application.

Optparse was a really similar alternative and it could be it, unless I found click.

Click library is a wrapper of (or framework based on) optparse. So you don't need to compare them, 'cause click will always be better, wider and easier.

Let's then describe click and why it's better than argparse (except argparse is kinda stupid already).

(+) Click has nice decorator syntax to create parsers (commands)

(+) Automatically generates help messages (but they were disabled, 'cause '--help' option unconditionally exits program)

(+) Has built-in messages for help to use a command (i.e. illegal option ...)

The following are the only pros which were affecting me.
