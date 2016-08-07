from . import Command
from ..val import sv, VAR
import es
import time
from cvars import cvar
from es_emulator.helpers import _can_change
from es_emulator.helpers import atof

@Command(syntax='<varname>', types=VAR, desc='Stores the server time in a variable.')
def gettime(argv):
  sv[argv[0]] = int(time.time())

@Command(syntax='<varname>', types=VAR, desc='Stores a timestamp in seconds in a variable. gettimestamp provides a shorter timestamp only for comparing against other es_gettimestamp values.')
def gettimestamp(argv):
  sv[argv[0]] = int(time.time() - 1136049334)

@Command(syntax='<varname>', types=VAR, desc='Stores the server time string in a variable.')
def gettimestring(argv):
  sv[argv[0]] = time.strftime(es.getString('eventscripts_timeformat'))

@Command(pre=False, desc='profile begin <var>\nor\nprofile end <var>')
def profile(argv):
  operation = argv[0] if len(argv) > 0 else ''
  var_name = argv[1] if len(argv) > 1 else ''
  if operation.lower() == 'begin':
    es.dbgmsg(1, 'Profiler timer {} started.'.format(var_name))
    es.setString(var_name, str(time.time()))
  else:
    var = cvar.find_var(var_name)
    if var is None:
        es.dbgmsg(0, 'The var "{}" could not be found'.format(var_name))
        return

    if not _can_change(var):
        return

    now = time.time()
    diff = now - atof(var.get_string())
    es.dbgmsg(2, 'Profiler: {} - {} = {}'.format(now, var.get_string(), diff))
    var.set_float(diff)
    es.dbgmsg(1, 'Profiler timer {} ended: {}'.format(var_name, diff))
