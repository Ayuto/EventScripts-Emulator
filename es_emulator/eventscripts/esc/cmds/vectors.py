from . import Command

@Command(con=True, desc='Creates a vector-string that goes from point/vector A to point/vector B.')
def createvectorfrompoints(argv):
  pass

@Command(con=True, desc='Creates a string form of three x y z variables representing a vector.')
def createvectorstring(argv):
  pass

@Command(con=True, desc='Stores the vector\'s current x, y, and z as read from the vector in string form.')
def splitvectorstring(argv):
  pass

@Command(con=True, desc='Returns the gravity vector.')
def getgravityvector(argv):
  pass
