import es
from ..val import sv, VAR
from . import Command

@Command(syntax='<var> <type> [optional] [optional] <name-to-check>', types=VAR, desc='Checks whether a keygroup, keys, variable, or function exists.')
def exists(argv):
  var = argv[0]
  if argv[1] == 'variable':
    sv[var] = int(sv.exists(argv[2]))
  else:
    sv[var] = int(es.exists(*argv[1:]))

@Command(syntax='<varname> <userid>', desc='Stores the player\'s money value in a variable. (CS:S only)')
def getmoney(argv):
  arg_string = ' '.join(argv)
  pre_parsed_command = 'es_xgetplayerprop {} CCSPlayer.m_iAccount'.format(arg_string)
  es.dbgmsg(2, 'es_xgetmoney executing: {}'.format(pre_parsed_command))
  es.InsertServerCommand(pre_parsed_command)

@Command(syntax='<variable> [string]', desc='Looks-up a userid based on the string provided. Checks it against a userid, steamid, exact name, and partial name. (Based on Mani\'s algorithm.)')
def getuserid(argv):
  es.getuserid(*argv)

@Command(syntax='<var> <userid> <varname>', types=VAR, desc='Reads a console variable from a given player.')
def getclientvar(argv):
  result = es.getclientvar(*argv[1:])
  if result is not None:
    sv[argv[0]] = result

@Command(syntax='<keygroupname> [entity-class]', desc='Creates a keygroup for an entity class or for all entities.')
def createentitylist(argv):
  es.createentitylist(*argv)

@Command(syntax='<keygroup> [userid]', desc='Creates a new keygroup containing the current list of players.')
def createplayerlist(argv):
  es.createplayerlist(*argv)

@Command(syntax='<var> [team number]', types=VAR, desc='Stores the count of players on the server into a variable. Optionally a team can be specified. Returns -1 on error.')
def getplayercount(argv):
  result = es.getplayercount(*argv[1:])
  if result is not None:
    sv[argv[0]] = result

@Command(syntax='<var> [team number]', types=VAR, desc='Stores the count of living players on the server into a variable. Optionally a team can be specified. Returns -1 on error.')
def getlivingplayercount(argv):
  result = es.getlivingplayercount(*argv[1:])
  if result is not None:
    sv[argv[0]] = result

@Command(syntax='<var>', types=VAR, desc='Stores the maximum number of player slots the server allows.')
def getmaxplayercount(argv):
  sv[argv[0]] = es.getmaxplayercount(*argv[1:])

@Command(syntax='<var forwardmove> <var sidemove> <var upmove> <userid>', types=(VAR, VAR, VAR), desc='Stores the player\'s current forward movement value, side movement value, and upward movement value (in 3 different variables).')
def getplayermovement(argv):
  result = es.getplayermovement(*argv[3:])
  if result is not None:
    sv[argv[0]] = result[0]
    sv[argv[1]] = result[1]
    sv[argv[2]] = result[2]

@Command(syntax='<var x> <var y> <var z> <userid>', desc='Stores the player\'s current x, y, and z location (in 3 different variables).')
def getplayerlocation(argv):
  es.getplayerlocation(*argv)

@Command(syntax='<var> <userid>', desc='Checks a userid to see if it\'s a bot, stores 1 in the variable if so, 0 if not.')
def isbot(argv):
  es.isbot(*argv)

@Command(syntax='<var> <userid>', types=VAR, desc='Stores the player\'s name in the variable.')
def getplayername(argv):
  result = es.getplayername(*argv[1:])
  if result is not None:
    sv[argv[0]] = result

@Command(syntax='<var> <userid>', desc='Stores the player\'s STEAMID in the variable.')
def getplayersteamid(argv):
  es.getplayersteamid(*argv)

@Command(syntax='<var> <userid>', desc='Stores the player\'s team # in the variable.')
def getplayerteam(argv):
  es.getplayerteam(*argv)

@Command(syntax='<keygroup> [scriptname]', desc='Creates a new keygroup containing the current list of scripts.')
def createscriptlist(argv):
  pass

@Command(syntax='<variable>', types=VAR, desc='Returns the name of the Source game being played.')
def getgame(argv):
  sv[argv[0]] = es.getgame(*argv[1:])

@Command(syntax='<userid> <variable-name>', desc='Sends a request to query a client\'s console variable.')
def queryclientvar(argv):
  es.queryclientvar(*argv)
