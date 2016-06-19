from . import Command
import es

@Command(syntax='<emitter-type> <id> <sound> <volume> <attenuation> [flags] [pitch]', desc='Plays a sound from an entity.')
def emitsound(argv):
  es.emitsound(*argv)

@Command(syntax='<userid> <sound> [volume]', desc='Plays a sound to a player.')
def playsound(argv):
  es.playsound(*argv)

@Command(syntax='<soundpath>', desc='Precache sound.')
def precachesound(argv):
  es.precachesound(*argv)
  
@Command(syntax='<userid> <percent> <fadetime> <holdtime> <fadeintime>', desc='Fades the volume for a client.')
def fadevolume(argv):
  es.fadevolume(*argv)
  
@Command(syntax='<userid> <soundname>', desc='Stops a specific sound for a player.')
def stopsound(argv):
  es.stopsound(*argv)
