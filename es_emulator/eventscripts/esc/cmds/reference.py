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

@Command(con=True, desc='Stores the player\'s money value in a variable. (CS:S only)')
def getmoney(argv):
  pass
  
@Command(con=True, desc='Looks-up a userid based on the string provided. Checks it against a userid, steamid, exact name, and partial name. (Based on Mani\'s algorithm.)')
def getuserid(argv):
  pass
  
@Command(con=True, desc='Reads a console variable from a given player.')
def getclientvar(argv):
  pass
  
@Command(con=True, desc='Creates a keygroup for an entity class or for all entities.')
def createentitylist(argv):
  pass

@Command(con=True, desc='Creates a new keygroup containing the current list of players.')
def createplayerlist(argv):
  pass
  
@Command(con=True, desc='Stores the count of players on the server into a variable. Optionally a team can be specified. Returns -1 on error.')
def getplayercount(argv):
  pass

@Command(con=True, desc='Stores the count of living players on the server into a variable. Optionally a team can be specified. Returns -1 on error.')
def getlivingplayercount(argv):
  pass

@Command(con=True, desc='Stores the maximum number of player slots the server allows.')
def getmaxplayercount(argv):
  pass
  
@Command(con=True, desc='Stores the player\'s current forward movement value, side movement value, and upward movement value (in 3 different variables).')
def getplayermovement(argv):
  pass
  
@Command(con=True, desc='Stores the player\'s current x, y, and z location (in 3 different variables).')
def getplayerlocation(argv):
  pass

@Command(con=True, desc='Checks a userid to see if it\'s a bot, stores 1 in the variable if so, 0 if not.')
def isbot(argv):
  pass
  
@Command(con=True, desc='Stores the player\'s name in the variable.')
def getplayername(argv):
  pass

@Command(con=True, desc='Stores the player\'s STEAMID in the variable.')
def getplayersteamid(argv):
  pass

@Command(con=True, desc='Stores the player\'s team # in the variable.')
def getplayerteam(argv):
  pass
  
@Command(con=True, desc='Creates a new keygroup containing the current list of scripts.')
def createscriptlist(argv):
  pass
  
@Command(con=True, desc='Returns the name of the Source game being played.')
def getgame(argv):
  pass
  
@Command(con=True, desc='Sends a request to query a client\'s console variable.')
def queryclientvar(argv):
  pass
