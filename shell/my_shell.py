#! /usr/bin/env python3

import os, sys, time, re
from my_readLine import my_readLine

# Set prompt to '$' if not set
def set_prompt():
    if not os.environ["PS1"]:
        os.environ["PS1"] = '$'

# Change directory
def my_cd(args):
    if len(args) == 1 or len(args) > 2: # If just cd or multiple args, then print invalid
        os.write(2, "Invalid argument for command cd\n".encode())
    else:                               # Try changing dir if available
        try:
            os.chdir(args[1])
        except:
            os.write(2, ("\"%s\" is not an available directory\n" % args[1]).encode())

# Determine input redirection and piping
def process_data(*args):
    rc = os.fork()                    # create a new process to handle input
    if rc < 0:                        # Failed forking, terminate with error 1
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:                     # Child
        if type(args) == tuple:       # If came from a pipe, set fd to buffer
            os.close(1)
            os.dup(args[2])           # duplicate pw
            os.close(args[1])         # close pr
            os.close(args[2])         # close pw
        if '>' in args:               # If '>', redirect output
            redirect_out(args)
        if '<' in args:               # If '<', redirect input
            redirect_in(args)
        if '|' in args:               # If '|', pipe command
            my_pipe()
        else:
            execute_cmd(args)         # execute command (args)
    else:                             # Parent (forked ok)
        if type(args) == tuple:       # If came from a pipe, reset fd
            os.close(0)
            os.dup(args[1])           # duplicate pr
            os.close(args[1])         # close pr
            os.close(args[2])         # close pw

# Redirects fd 1 to file
def redirect_out(args):
    if '|' in args and args.index('>') < args.index('|'): # check for a > f | b
        os.write(2, "Output redirect, '>', can only be for the last subcommand of a pipe".encode())
        continue
    os.close(1)                                           # Close display fd and replace it with file
    os.open(args[args.index('>')+1], os.O_CREAT | os.O_WRONLY);
    os.set_inheritable(1, True)
    args.remove(args[args.index('>')+1])                  # Remove '>' from argument
    args.remove('>')

# Redirects fd 0 to file
def redirect_in(args):
    if '|' in args and args.index('>') < args.index('|'): # check for a | b < f
        os.write(2, "Input redirect, '<', can only be for the first subcommand of a pipe".encode())
        continue
    os.close(0)                                           # Close keyboard fd and replace it with file
    os.open(args[args.index('<')+1], os.O_RDONLY);
    os.set_inheritable(0, True)
    args.remove(args[args.index('<') + 1])                # Remove '<' from argument
    args.remove('<')

# Pipes two or more commands by a shared buffer
def my_pipe(args):
    pr, pw = os.pipe() # Get fds for pipe read/write buffer
    for f in (pr, pw):
        os.set_inheritable(f, True)

    pargs = ""         # Tokenize args for pipe
    for i in args:
        pargs += i     # Convert into a single list
    pargs.split('|')   # Tokenize left and right sides and sent them to process_data() with pr, pw
    process_data(pargs[0], pr,pw)
    process_data(pargs[1], pr,pw)

# Executes given command if available
def execute_cmd(args):                            # Execute command
    for dir in re.split(":", os.environ['PATH']): # Try each directory in the path
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ)  # Try to exec program
        except FileNotFoundError:                 # ...expected
            pass                                  # ...fail quietly

    os.write(1, ("\"%s\" is not an available command in your system\n" % args[0]).encode())
    sys.exit(2)                                   # If not a cmd, terminate with error 2

# MAIN
set_prompt()
while(True):                                        # Loop forever
    os.write(1,("%s" % os.environ["PS1"]).encode()) # Print shell prompt
    args = my_readLine().split()                    # Get and tokenize input

    if args == []:                                  # If no input, continue
        continue
    elif args[0] == "exit":                         # If input is exit, then exit
        sys.exit(0)
    elif args[0] == "cd":                           # If input is cd, then change directory
        my_cd(args)
        continue
    else:                                           # Handle any other input
        process_data(args)
