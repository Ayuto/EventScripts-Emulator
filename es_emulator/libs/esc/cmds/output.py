import es
from ..val import sv, VAR
from . import Command

@Command(con=True, desc='Broadcasts a message to all players. Will not expand any EventScripts variables. If the first word of the message is \'GREEN\', or \'LIGHTGREEN\' then the message is displayed in that color.')
def msg(argv):
  pass
  
@Command(con=True, desc='Sends HUD message to one player. If the first word of the message is \'#green\', or \'#lightgreen\' then the message is displayed in that color.')
def tell(argv):
  pass
  
@Command(con=True, desc='Sends HUD message to one player.')
def toptext(argv):
  pass
  
@Command(con=True, desc='Sends an AMX-Style menu to the users')
def menu(argv):
  pass
  
@Command(con=True, desc='Sends an ESC menu to a player.')
def escmenu(argv):
  pass
  
@Command(con=True, desc='Sends a keygroup-based message to a player.')
def keygroupmsg(argv):
  pass

@Command(con=True, desc='Sends an ESC textbox to a player.')
def esctextbox(argv):
  pass

@Command(con=True, desc='Sends an ESC input box to a player.')
def escinputbox(argv):
  pass
  
@Command(con=True, desc='Broadcasts a centered HUD message to all players.')
def centermsg(argv):
  pass

@Command(con=True, desc='Sends a centered HUD message to all players.')
def centertell(argv):
  pass
  
@Command(con=True, desc='Create and send a usermsg to a client.')
def usermsg(argv):
  pass
  
@Command(con=True, desc='Prints a debug message for EventScripts.')
def dbgmsg(argv):
  pass
  
@Command(con=True, desc='Prints a debug message for EventScripts')
def dbgmsgv(argv):
  pass

@Command(syntax='<message>', desc='Logs a message to the server log.')
def log(args):
  es.dbgmsg(0, args)
  es.log(args)
  
@Command(types=VAR, syntax='<message>', desc='Logs the text inside of a variable.')
def logv(argv):
  result = str(sv[argv[0]])
  es.dbgmsg(0, result)
  es.log(result)

@Command(con=True, desc='Logs a message to the server log. Will not expand any EventScripts variables. Allows quotes.')
def logq(argv):
  pass
  
@Command(con=True, desc='Lists the script packs running on the server. If a userid is provided, will es_tell the list to the user.')
def scriptpacklist(argv):
  pass
