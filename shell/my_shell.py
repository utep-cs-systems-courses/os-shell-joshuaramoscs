#! /usr/bin/env python3

import os, sys, time, re
from my_readLine import my_readLine

def executeCmd(args):                             # Function to execute command
    for dir in re.split(":", os.environ['PATH']): # Try each directory in the path
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ)  # try to exec program
        except FileNotFoundError:                 # ...expected
            pass                                  # ...fail quietly

    os.write(1, ("\"%s\" is not an available command in your system\n" % args[0]).encode())
    sys.exit(2)                                   # terminate with error 2

# MAIN
if not os.environ["PS1"]:             # If prompt is not set, then set it to '$'
    os.environ["PS1"] = '$'

while(True):                          # Loop forever
    os.write(1,("%s" % os.environ["PS1"]).encode()) # Print shell prompt
    args = my_readLine().split()      # Tokenize input

    if args == []:                    # If no input, continue
        continue
    elif args[0] == "exit":           # If input is exit, then exit
        sys.exit(0)
    elif args[0] == "cd":             # If input is cd, then change directory
        if len(args) == 1 or len(args) > 2:
            os.write(2, "Invalid argument for command cd\n".encode())
        else:
            try:
                os.chdir(args[1])
            except:
                os.write(2, ("\"%s\" is not an available directory\n" % args[1]).encode())
        continue

    rc = os.fork()                                    # create a new process

    if rc < 0:                                        # Failed forking
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)                                   # Terminate with error 1

    elif rc == 0:                                     # Child
        if '>' in args:                               # Redirect child's fd output
            os.close(1)                               # Close display fd and replace it with file
            os.open(args[args.index('>')+1], os.O_CREAT | os.O_WRONLY);
            os.set_inheritable(1, True)
            args.remove(args[args.index('>')+1])      # Remove '>' from argument
            args.remove('>')
        if '<' in args:                               # Redirect child's fd input
            os.close(0)                               # Close keyboard fd and replace it with file
            os.open(args[args.index('<')+1], os.O_RDONLY);
            os.set_inheritable(0, True)
            args.remove(args[args.index('<') + 1])    # Remove '<' from argument
            args.remove('<')

        executeCmd(args)                              # execute command in args

    else:                                             # Parent (forked ok)
        childPidCode = os.wait()
