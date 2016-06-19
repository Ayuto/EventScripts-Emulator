from . import Command
import es

@Command(syntax='<output-var> <vectorstring-A> <vectorstring-B>', desc='Creates a vector-string that goes from point/vector A to point/vector B.')
def createvectorfrompoints(argv):
  es.createvectorfrompoints(*argv)

@Command(syntax='<output-var> <x> <y> <z>', desc='Creates a string form of three x y z variables representing a vector.')
def createvectorstring(argv):
  es.createvectorstring(*argv)

@Command(syntax='<var x> <var y> <var z> <vectorstring>', desc='Stores the vector\'s current x, y, and z as read from the vector in string form.')
def splitvectorstring(argv):
  es.splitvectorstring(*argv)

@Command(syntax='<var>', desc='Returns the gravity vector.')
def getgravityvector(argv):
  es.getgravityvector(*argv)
