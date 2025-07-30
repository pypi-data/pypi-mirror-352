#
# Portable way of printing to stderr in python, works same as built-in function 'print'
#
# Source: https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python#answer-14981125
#
from __future__ import print_function
import sys    

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
