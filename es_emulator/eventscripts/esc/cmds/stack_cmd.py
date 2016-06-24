from . import Command
from ..val import sv
import es
from cvars import cvar

stacks = {}

def _create_stack(argv):
  name = argv[1]
  if name in stacks:
    es.dbgmsg(0, 'The stack {} already exists.'.format(name))
  else:
    stacks[name] = []

def _delete_stack(argv):
  name = argv[1]
  stacks.pop(name, 0)

def _save_stack(argv):
  var_name = argv[2] if len(argv) > 1 else ''
  var = cvar.find_var(var_name)
  if var is not None:
    name = argv[1]
    try:
      stack = stacks[name]
    except KeyError:
      es.dbgmsg(0, 'The stack {} couldn\'t be found.'.format(name))
    else:
      stack.append(var.get_string())
  else:
    es.dbgmsg(0, 'The variable {} does not exist.'.format(var_name))

def _restore_stack(argv):
  name = argv[1]
  try:
    stack = stacks[name]
  except KeyError:
    es.dbgmsg(0, 'The stack {} couldn\'t be found.'.format(name))
  else:
    if stack:
      value = stack.pop()
      var_name = argv[2] if len(argv) > 1 else ''
      var = cvar.find_var(var_name)
      if var is not None:
        var.set_string(value)
      else:
        es.dbgmsg(0, 'The var "{}" could not be set'.format(var_name))
    else:
      es.dbgmsg(0, 'stack: ERROR: Pop attempt when stack empty: {}'.format(name))

def _pop_stack(argv):
  name = argv[2] if len(argv) > 1 else ''
  try:
    stack = stacks[name]
  except KeyError:
    es.dbgmsg(0, 'The stack {} couldn\'t be found.'.format(name))
  else:
    if stack:
      value = stack.pop()
      var_name = argv[1]
      var = cvar.find_var(var_name)
      if var is not None:
        var.set_string(value)
      else:
        es.dbgmsg(0, 'The var "{}" could not be set'.format(var_name))
    else:
      es.dbgmsg(0, 'stack: ERROR: Pop attempt when stack empty.')

def _push_stack(argv):
    name = argv[1]
    try:
      stack = stacks[name]
    except KeyError:
      es.dbgmsg(0, 'The stack {} couldn\'t be found.'.format(name))
    else:
      stack.append(argv[2] if len(argv) > 1 else '')

def _get_stack_length(argv):
    name = argv[2] if len(argv) > 1 else ''
    try:
      stack = stacks[name]
    except KeyError:
      es.dbgmsg(0, 'The stack {} couldn\'t be found.'.format(name))
    else:
      var_name = argv[1]
      var = cvar.find_var(var_name)
      if var is not None:
        var.set_string(str(len(stack)))
      else:
        es.dbgmsg(0, 'The var "{}" could not be set'.format(var_name))

@Command(pre=False, syntax='<operation> <stack id/variable> [stack id/value/variable]', desc='Allows you to do various stack operations with a named stack. Supports create, delete, pop, push, getlength.')
def stack(argv):
  operation = argv[0].lower()
  if operation == 'create':
    _create_stack(argv)
  elif operation == 'delete':
    _delete_stack(argv)
  elif operation == 'save':
    _save_stack(argv)
  elif operation == 'restore':
    _restore_stack(argv)
  elif operation == 'pop':
    _pop_stack(argv)
  elif operation == 'push':
    _push_stack(argv)
  elif operation == 'getlength':
    _get_stack_length(argv)