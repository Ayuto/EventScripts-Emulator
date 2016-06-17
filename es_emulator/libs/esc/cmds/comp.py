import es, esc
from gamethread import queue
from .. import aliases, stack
from . import Command, Alias
from ..val import sv

@Command(syntax='[commandname] [[commands]]', pre=False, argsfrom=1, desc='Alias a command.')
def alias(argv, args):
  if not argv:
    es.dbgmsg(0, 'Current alias commands:\n')
    for alias in aliases:
      cmdstring = '; '.join('%s %s' % (cmdname, args) for cmdname, argv, args in aliases[alias])
      es.dbgmsg(0, '%s : %s\n' % (alias, cmdstring))
  else:
    name = argv[0]
    if name in aliases:
      aliases[name].getcode(args, stack.currentline)
    elif not es.exists('command', argv[0]):
      Alias(name).getcode(args, stack.currentline)
    else:
      raise RuntimeError, 'Attempt to alias over an already registered command failed (current ESC limitation)'
    
@Command(pre=False, reg=False)
def wait(desc='Delay code execution for one tick'):
  if sv.eventscripts_currentmap:
    stack.kill()
    sv.save()
    queue(stack.runall)
      
@Command(pre=False, reg=False, desc='Kills code execution. Very bad. Debug only.')
def die():
  stack.kill()
  es.dbgmsg(0, 'ESC code execution killed')

@Command(pre=False, desc='Runs unittest/unittest.cfg')
def unittest():
  stack.insertrawlines(map(str.strip, open('%s/unittest/unittest.cfg' % sv('eventscripts_addondir')).xreadlines()))
