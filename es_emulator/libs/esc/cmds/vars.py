import re, es, esc
from . import Command
from ..val import sv, STR, INT, VAR

@Command(syntax='<key> <value> [description]', desc='Adds a new server/global variable.')
def _set(argv):
  var, val = argv[:2]
  if len(argv) > 2 and not sv.exists(var):
    es.set(var, val, argv[2])
  sv[var] = val
  
@Command(syntax='<key> <value> [description]', desc='Adds a new server/global variable.')
def setinfo(argv):
  var, val = argv[:2]
  if len(argv) > 2 and not sv.exists(var):
    es.set(var, val, argv[2])
  sv[var] = val
  
@Command(syntax='<variable>', types=VAR, desc='Makes a console variable public such that changes to it are announced to clients.')
def makepublic(argv):
  es.makepublic(argv[0])
  
@Command(syntax='<varname> <varname2>', types=(VAR, VAR), desc='Reads the server variable referenced by varname2 and copies it into the variable referenced by varname.')
def copy(argv):
  sv[argv[0]] = sv[argv[1]].strval
    
def _format_rep(match, tokens, expand=False):
  result = tokens[int(match.group(1))]
  if expand:
    return str(sv(result))
  return str(result)

FORMAT_REGEX = [re.compile('%%([1-%s])' % i) for i in xrange(1, 10)]

@Command(syntax='<variable> <format-string> [token1] [token2] [...] [tokenN]', desc='Allows you to format a string by filling in a list of strings into a format string.')
def _format(argv):
  (var, formatstring), tokens = argv[:2], argv[1:11]
  if tokens:
    sv[var] = FORMAT_REGEX[len(tokens)].sub(lambda match: _format_rep(match, tokens), formatstring)
  else:
    sv[var] = formatstring
  
@Command(syntax='<variable> <format-string> [token1] [token2] [...] [tokenN]', desc='Allows you to format a string by filling in a list of strings into a format string.')
def formatv(argv):
  (var, formatstring), tokens = argv[:2], argv[1:11]
  if tokens:
    sv[var] = FORMAT_REGEX[len(tokens)].sub(lambda match: _format_rep(match, tokens, expand=True), formatstring)
  else:
    sv[var] = formatstring

@Command(con=True, desc='Allows you to format a string by filling in a list of strings into a format string.')
def formatqv(argv):
  pass

@Command(syntax='<variable> <operator> <value1> [value2]', types=VAR, desc='EventScripts string functions, experimental support originally written by Cr3V3TT3')
def string(argv):
  
  var = argv[0]
  op, one = argv[1:3]
  if op in ('replace', 'replacev'):
    rep = argv[3] if len(argv) > 3 else ''
    if op == 'replacev':
      one, rep = sv(one), sv(rep)
    sv[var] = sv[var].replace(one, rep)
  elif op == 'section':
    sv[var] = sv[var][int(one):None if len(argv) < 4 else int(argv[3])]
  else:
    raise SyntaxError, 'unknown fucntion "%s"' % op
    

@Command(syntax='<variable> <string> <token#> [tokenchar]', types=(VAR, STR, INT), desc='Set a variable to a particular token in the string.')
def token(argv):
  sep = ' '
  if len(argv) > 3:
    sep = argv[3]
  n = argv[2]
  tokens = str(argv[1]).split(sep)
  if not n:
    sv[argv[0]] = len(tokens)
  else:
    if len(tokens) < n:
      raise ValueError, 'the specified token number does not exist'
    sv[argv[0]] = tokens[n-1]
  
@Command(syntax='<key> <value>', desc='Forces a variable to a particular value')
def forcevalue(argv):
  var, val = argv[:2]
  es.forcevalue(var, val)
  sv[var] = val

@Command(con=True, desc='Adds or removes the cheat flag from a command or variable. (EXPERIMENTAL/UNSUPPORTED)')
def flags(argv):
  pass

@Command(con=True, desc='Compares two strings.')
def strcmp(argv):
  pass

@Command(con=True, desc='Returns the length of a string.')
def strlen(argv):
  pass
  
@Command(con=True, desc='Sets a convar value for a fake client.')
def botsetvalue(argv):
  pass
  
@Command(con=True, desc='Various regular expression commands.')
def regex(argv):
  pass
