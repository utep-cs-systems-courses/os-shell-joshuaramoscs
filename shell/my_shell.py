#! /usr/bin/env python3

import os, sys, time, re
from my_readLine import my_readLine

while(True):                          # Loop forever
    os.write(1,"my_shell:$ ".encode()) # Print shell prompt
    args = my_readLine().split()      # Tokenize input

    if args == []:                    # If no input, continue
        continue
    
    elif args[0] == "exit":           # If input is exit, then exit
        sys.exit(0)
    
    # pid = os.getpid()               # Uncomment this and all os.write() to see forking
    # os.write(1, ("About to fork (pid:%d)\n" % pid).encode())

    rc = os.fork()

    if rc < 0:                                        # Failed forking
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)                                   # Terminate with error

    elif rc == 0:                                     # Child
        # os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % (os.getpid(), pid)).encode())
        for dir in re.split(":", os.environ['PATH']): # Try each directory in the path
            program = "%s/%s" % (dir, args[0])
            # os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
            try:
                os.execve(program, args, os.environ)  # try to exec program
            except FileNotFoundError:                 # ...expected
                pass                                  # ...fail quietly

        # os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
        os.write(1, ("\"%s\" is not an available command in your system.\n" % args[0]).encode())
        sys.exit(1)                                   # terminate with error

    else:                                             # Parent (forked ok)
        # os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % (pid, rc)).encode())
        childPidCode = os.wait()
        # os.write(1, ("Parent: Child %d terminated with exit code %d\n" % childPidCode).encode())
