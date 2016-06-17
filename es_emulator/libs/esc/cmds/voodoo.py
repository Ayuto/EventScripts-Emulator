from . import Command

@Command(con=True, desc='Fires an entity trigger.')
def fire(argv):
  pass
  
@Command(con=True, desc='Sets a server class property for the given entity index')
def setindexprop(argv):
  pass

@Command(con=True, desc='Sets a server class property for the given player')
def setplayerprop(argv):
  pass
  
@Command(con=True, desc='Miscellaneous tricky things.')
def trick(argv):
  pass

@Command(con=True, desc='Gives the player a named item.')
def give(argv):
  pass

@Command(con=True, desc='Creates an entity where a player is looking.')
def entcreate(argv):
  pass
  
@Command(con=True, desc='Interface with the Source physics engine (physics gravity, object velocity, etc).')
def physics(argv):
  pass
  
@Command(con=True, desc='Gets the index for the first named entity found by that name. Returns -1 if not found.')
def getentityindex(argv):
  pass
  
@Command(con=True, desc='Gets a server class property for a particular player')
def getplayerprop(argv):
  pass

@Command(con=True, desc='Gets a server class property for a particular entity index')
def getindexprop(argv):
  pass
  
@Command(con=True, desc='Precache a decal and return its index.')
def precachedecal(argv):
  pass

@Command(con=True, desc='Precache a model and return its index.')
def precachemodel(argv):
  pass
  
@Command(con=True, desc='Gets the handle for a player class property using an entity handle (Untested)')
def getplayerhandle(argv):
  pass

@Command(con=True, desc='Names the entity the player is looking at. (DOES NOT SET PLAYER NAME)')
def entsetname(argv):
  pass

@Command(con=True, desc='Removes an entity class')
def remove(argv):
  pass
  
@Command(con=True, desc='Dumps to the console all server classes.')
def dumpserverclasses(argv):
  pass
  
@Command(con=True, desc='Dumps to console all server classes and properties for all entities.')
def dumpentities(argv):
  pass
  
@Command(con=True, desc='Set light style.')
def lightstyle(argv):
  pass
