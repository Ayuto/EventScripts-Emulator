from . import Command

@Command(con=True, desc='Plays a sound from an entity.')
def emitsound(argv):
  pass

@Command(con=True, desc='Plays a sound to a player.')
def playsound(argv):
  pass

@Command(con=True, desc='Precache sound.')
def precachesound(argv):
  pass
  
@Command(con=True, desc='Fades the volume for a client.')
def fadevolume(argv):
  pass
  
@Command(con=True, desc='Stops a specific sound for a player.')
def stopsound(argv):
  pass
