from .. import stack
from ..parse import tokenize
from . import Command

@Command(expand=True, pre=False, syntax='<commandstring>', desc='Mattie\'s EventScripts variable parsing.\nusage: es <command string>\nThis will execute <command string> after parsing it for items like event_var() and server_var() and replacing them with the appropriate value.')
def _es(argv):
  stack.insertline(argv[0], argv[1:])
  
@Command(expand=True, remquotes=True, pre=False, syntax='<commandstring>', desc='Mattie\'s EventScripts variable parsing, without quotation marks.\nusage: esnq <command string>\nThis will execute <command string> after parsing it for items like event_var() and server_var() and replacing them with the appropriate value. WARNING: Removes all quotation marks.')
def esnq(argv, args):
  if not ';' in args:
    args = args.replace('"', '')
    argv = tokenize(args)
  stack.insertline(argv[0], argv[1:], args)
  
@Command(pre=False, remquotes=True, syntax='<commandstring>', desc='Remove quotation marks.\nusage: es_xnq <command string>\nThis will execute <command string> after removing quotation marks. WARNING: Removes all quotation marks.')
def es_xnq(args):
  args = args.replace('"', '')
  argv = tokenize(args)
  stack.insertline(argv[0], argv[1:], args)
