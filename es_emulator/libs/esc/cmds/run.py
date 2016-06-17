import gamethread, esc
from gamethread import queue, delayed
from .. import stack
from ..val import sv, FLOAT, VAR
from . import Command

@Command(syntax='<variable>', types=VAR, desc='Just runs a command-string inside of the variable.')
def commandv(argv):
  stack.insertrawline(sv(argv[0]))
  
@Command(argsfrom=2, syntax='<seconds> <commandstring>', types=FLOAT, desc='Will run <commandstring>, after <seconds> seconds.')
def delayed(argv, args):
  gamethread.delayed(argv[0], stack.queueline, (argv[1], argv[2:], args, esc.stack.currentblock, True))

@Command(syntax='<commandstring>', desc='Adds a command to the end of the command queue.')
def soon(argv, args):
  queue(stack.queueline, (argv[0], argv[1:], args, esc.stack.currentblock, True))
