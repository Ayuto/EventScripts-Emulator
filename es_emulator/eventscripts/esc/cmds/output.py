import es
from ..val import sv, VAR
from . import Command
from engines.server import engine_server
from es_emulator.helpers import atoi

@Command(syntax='[color] <msg>', desc='Broadcasts a message to all players. Will not expand any EventScripts variables. If the first word of the message is \'GREEN\', or \'LIGHTGREEN\' then the message is displayed in that color.')
def msg(argv):
  es.msg(*argv)

@Command(syntax='<userid> [color] <msg>', desc='Sends HUD message to one player. If the first word of the message is \'#green\', or \'#lightgreen\' then the message is displayed in that color.')
def tell(argv):
  es.tell(*argv)

@Command(syntax='<userid> <duration> [color] <message>', desc='Sends HUD message to one player.')
def toptext(argv):
  es.toptext(*argv)

@Command(syntax='<duration> <userid> <msg> [options]', desc='Sends an AMX-Style menu to the users')
def menu(argv):
  es.menu(*argv)

@Command(syntax='<time> <userid> <title> <text> <button1> [button...] [button8]', desc='Sends an ESC menu to a player.')
def escmenu(argv):
  es.escmenu(*escmenu)

@Command(syntax='<userid> <type> <keygroup>', desc='Sends a keygroup-based message to a player.')
def keygroupmsg(argv):
  es.keygroupmsg(*argv)

@Command(syntax='<time> <userid> <title> <text>', desc='Sends an ESC textbox to a player.')
def esctextbox(argv):
  es.esctextbox(*argv)

@Command(syntax='<time> <userid> <title> <text> <command>', desc='Sends an ESC input box to a player.')
def escinputbox(argv):
  es.escinputbox(*argv)

@Command(syntax='<msg>', desc='Broadcasts a centered HUD message to all players.')
def centermsg(argv):
  es.centermsg(*argv)

@Command(syntax='<userid> <msg>', desc='Sends a centered HUD message to all players.')
def centertell(argv):
  es.centertell(*argv)

@Command(syntax='<operation> [data-type] <msg-name> [value]', desc='Create and send a usermsg to a client.')
def usermsg(argv):
  es.usermsg(*argv)

@Command(syntax='<level> <msg>', desc='Prints a debug message for EventScripts.')
def dbgmsg(argv):
  if len(argv) > 1:
    es.dbgmsg(atoi(argv[0]), ' '.join(argv[1:]))
  else:
    raise SyntaxError

@Command(syntax='<level> <variable>', desc='Prints a debug message for EventScripts')
def dbgmsgv(argv):
  es.dbgmsgv(*argv)

@Command(syntax='<message>', desc='Logs a message to the server log.')
def log(argv):
  es.log(*argv)

@Command(syntax='<message>', desc='Logs the text inside of a variable.')
def logv(argv):
  es.logv(*argv)

@Command(syntax='<msg>', desc='Logs a message to the server log. Supports expanding EventScripts variables. Allows quotes.')
def logq(argv):
  engine_server.log_print(' '.join(argv) + '\n')

@Command(syntax='[userid]', desc='Lists the script packs running on the server. If a userid is provided, will es_tell the list to the user.')
def scriptpacklist(argv):
  es.scriptpacklist(*argv)
