from . import Command
from ..val import sv, VAR
import es

@Command(syntax='<output-var> <vectorstring-A> <vectorstring-B>', types=VAR, desc='Creates a vector-string that goes from point/vector A to point/vector B.')
def createvectorfrompoints(argv):
  sv[argv[0]] = es.createvectorfrompoints(*argv[1:])

@Command(syntax='<output-var> <x> <y> <z>', types=VAR, desc='Creates a string form of three x y z variables representing a vector.')
def createvectorstring(argv):
  sv[argv[0]] = es.createvectorstring(*argv[1:])

@Command(syntax='<var x> <var y> <var z> <vectorstring>', types=(VAR, VAR, VAR), desc='Stores the vector\'s current x, y, and z as read from the vector in string form.')
def splitvectorstring(argv):
  x, y, z = es.splitvectorstring(*argv[3:])
  sv[argv[0]] = x
  sv[argv[1]] = y
  sv[argv[2]] = z

@Command(syntax='<var>', desc='Returns the gravity vector.')
def getgravityvector(argv):
  sv[argv[0]] = es.getgravityvector()
