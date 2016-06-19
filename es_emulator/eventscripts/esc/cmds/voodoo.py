from . import Command
from ..val import sv, VAR
import es

@Command(syntax='<userid> <target> [action] [value] [delay]', desc='Fires an entity trigger.')
def fire(argv):
  es.fire(*argv)

@Command(syntax='<index> <propertypath> <value>', desc='Sets a server class property for the given entity index')
def setindexprop(argv):
  es.setindexprop(*argv)

@Command(syntax='<userid> <propertypath> <value>', desc='Sets a server class property for the given player')
def setplayerprop(argv):
  es.setplayerprop(*argv)

@Command(syntax='<operation> [parameters]', desc='Miscellaneous tricky things.')
def trick(argv):
  es.trick(*argv)

@Command(syntax='<userid> <entity>', desc='Gives the player a named item.')
def give(argv):
  es.give(*argv)

@Command(syntax='<userid> <entity>', desc='Creates an entity where a player is looking.')
def entcreate(argv):
  es.entcreate(*argv)

@Command(syntax='<command> [options]', desc='Interface with the Source physics engine (physics gravity, object velocity, etc).')
def physics(argv):
  # TODO
  es.physics(*argv)

@Command(syntax='<variable> <entity-name>', types=VAR, desc='Gets the index for the first named entity found by that name. Returns -1 if not found.')
def getentityindex(argv):
  sv[argv[0]] = es.getentityindex(*argv[1:])

@Command(syntax='<variable> <userid> <propertypath>', types=VAR, desc='Gets a server class property for a particular player')
def getplayerprop(argv):
  result = es.getplayerprop(*argv[1:])
  if result is not None:
    sv[argv[0]] = result

@Command(syntax='<variable> <index> <propertypath>', types=VAR, desc='Gets a server class property for a particular entity index')
def getindexprop(argv):
  result = es.getindexprop(*argv[1:])
  if result is not None:
    sv[argv[0]] = result

@Command(syntax='[var] <modelpath>', types=VAR, desc='Precache a decal and return its index.')
def precachedecal(argv):
  if len(argv) > 1:
    sv[argv[0]] = es.precachedecal(*argv[1:])
  else:
    es.precachedecal(*argv)

@Command(syntax='[var] <modelpath>', types=VAR, desc='Precache a model and return its index.')
def precachemodel(argv):
  if len(argv) > 1:
    sv[argv[0]] = es.precachemodel(*argv[1:])
  else:
    es.precachemodel(*argv)

@Command(syntax='<variable> <userid>', types=VAR, desc='Gets the handle for a player class property using an entity handle (Untested)')
def getplayerhandle(argv):
  sv[argv[0]] = es.getplayerhandle(*argv[1:])

@Command(syntax='<userid> <name>', desc='Names the entity the player is looking at. (DOES NOT SET PLAYER NAME)')
def entsetname(argv):
  es.entsetname(*argv)

@Command(syntax='<entity>', desc='Removes an entity class')
def remove(argv):
  es.remove(*argv)

@Command(desc='Dumps to the console all server classes.')
def dumpserverclasses(argv):
  es.dumpserverclasses()

@Command(desc='Dumps to console all server classes and properties for all entities.')
def dumpentities(argv):
  es.dumpentities()

@Command(syntax='<stylenum> <stylestring>', desc='Set light style.')
def lightstyle(argv):
  es.lightstyle(*argv)
