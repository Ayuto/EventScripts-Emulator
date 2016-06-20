from . import Command
from ..val import sv, VAR
import es
from cvars import cvar

@Command(syntax='<tablename> <string>', desc='Update an entry in a stringtable')
def stringtable(argv):
  es.stringtable(*argv)

@Command(syntax='<tablename> <string>', desc='Update an entry in a stringtable')
def dumpstringtable(argv):
  es.dumpstringtable(*argv)

@Command(pre=False, desc='Dump string tables.')
def es_dumpstringtables(argv):
  raise NotImplementedError

@Command(pre=False, desc='Dump UserMessage list for the Source mod.')
def es_dumpusermessages(argv):
  raise NotImplementedError

# es_xsql open <db> [dbdir]
# es_xsql close <db>
# es_xsql queryvalue <db> <single-result-var> "<SQL-string>"
# es_xsql query <db> [result-keygroup] "<SQL-string>"
@Command(syntax='<operation> <db> [var] [sql]', desc='Local database support')
def sql(argv):
  es.sql(*argv)

@Command(syntax='<db> <query>', desc='Does some SQL.')
def dosql(argv):
  es.dosql(*argv)

@Command(syntax='[declare] <pathtoeventfile>', desc='Reads an event file and registers EventScripts as a handler for those events.')
def loadevents(argv):
  es.loadevents(*argv)

@Command(syntax='<path/script>', desc='Runs an exec file from memory.')
def mexec(argv):
  es.mexec(*argv)

@Command(syntax='[var] <botname>', types=VAR, desc='Adds a bot to the server.')
def createbot(argv):
  if len(argv) > 1:
    result = es.createbot(*argv[1:])
    if result is not None:
      sv[argv[0]] = result
  else:
    es.createbot(*argv)

@Command(syntax='<mode> [options]', desc='Performs a particular effect.')
def effect(argv):
  es.effect(*argv)

@Command(syntax='<command> <event-name> [value-name] [value]', desc='Create and fire events to signal to plugins that an event has happened. It must be an event loaded via es_loadevents.')
def event(argv):
  es.event(*argv)

@Command(syntax='<variable>', desc='Returns 1 in the variable if the server a dedicated server.')
def isdedicated(argv):
  sv[argv[0]] = es.isdedicated()

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