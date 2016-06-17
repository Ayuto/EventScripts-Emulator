import es
from .. import stack
from ..parse import join
from ..val import sv, INT, VAR
from . import Command

@Command(syntax='<command-name> <block-name> [description]', desc='Adds a console command that refers to a particular block.')
def regcmd(argv):
  if es.exists('command', argv[0]):
    raise ValueError, 'command %s already exists' % argv[0]
  es.regcmd(*argv[:3])
  
@Command(syntax='<command-name> <block-name> [description]', desc='Adds a client command that refers to a particular block.')
def regclientcmd(argv):
  if es.exists('clientcommand', argv[0]):
    raise ValueError, 'command %s already exists' % argv[0]
  es.regclientcmd(*argv[:3])
  
@Command(syntax="<command>", desc='Removes a client command that refers to a particular block.')
def unregclientcmd(argv):
  if not es.exists('clientcommand', argv[0]):
    raise ValueError, 'did not find command: %s' % argv[0]
  es.unregclientcmd(argv[0])

@Command(syntax='<command-name> <block-name> [description]', desc='Adds a say command that refers to a particular block.')
def regsaycmd(argv):
  if es.exists('saycommand', argv[0]):
    raise ValueError, 'command %s already exists' % argv[0]
  es.regsaycmd(*argv[:3])
  
@Command(syntax="<command>", desc='Removes a say command that refers to a particular block.')
def unregsaycmd(argv):
  if not es.exists('saycommand', argv[0]):
    raise ValueError, 'did not find command: %s' % argv[0]
  es.unregsaycmd(argv[0])

@Command(syntax='<var> <index>', types=(VAR, INT), desc='Gets the command parameter passed to the current ES console command.')
def getargv(argv):
  sv[argv[0]] = stack.getargv(argv[1])
  
@Command(syntax='<var>', types=VAR, desc='Gets the commandstring passed to the current ES console command.')
def getargs(argv):
  sv[argv[0]] = stack.getargs()
  
@Command(syntax='<var>', types=VAR, desc='Gets the count of parameters passed to the current ES console command.')
def getargc(argv):
  sv[argv[0]] = stack.getargc()

@Command(syntax='<var>', types=VAR, desc='Gets the userid of the user that executed the command.')
def getcmduserid(argv):
  sv[argv[0]] = stack.getcmduserid()

