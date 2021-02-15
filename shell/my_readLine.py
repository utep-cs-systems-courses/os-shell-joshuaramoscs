#! /usr/bin/env python3

import os, sys, time, re

ibuf = ""      # Input buffer
sbuf = ""      # String buffer
sbufLength = 0 # String buffer length
currChar = 0   # Index of current char in sbuf

def my_getChar():
    global ibuf
    global sbuf
    global sbufLength
    global currChar
    
    if currChar == sbufLength: # If we reached the end of sbuf, get a new line and reset values
        ibuf = os.read(0, 100)
        sbuf = ibuf.decode()
        sbufLength = len(sbuf)
        currChar = 0
        if sbufLength == 0:    # If we reached the end of the input, return nothing
            return ''
    
    char = sbuf[currChar]
    currChar += 1
    return char

def my_readLine():
    char = my_getChar()
    line = ""
    
    while char != '\n':     # While char is not equal to new line, keep getting chars for line
        line += char
        char = my_getChar()
        if char == '':      # If char is empty, then we reached EOF; retun
            return line
    line+= '\n'             # If a new line was found, then return the line with a new line char
    return line
