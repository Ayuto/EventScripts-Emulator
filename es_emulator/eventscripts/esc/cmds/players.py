from . import Command
import es

@Command(syntax='<command> [variable] <to_userid> <from_userid>', desc='Allows you to control listening players.')
def voicechat(argv):
  es.voicechat(*argv)

@Command(syntax='<userid> <commandstring>', desc='Forces a userid to execute a command in their console.')
def cexec(argv):
  es.cexec(*argv)

@Command(syntax='<commandstring>', desc='Forces all users to execute a command in their console.')
def cexec_all(argv):
  es.cexec_all(*argv)

@Command(syntax='<userid> <commandstring>', desc='Forces a userid to execute a command on the server console (bypassing client console).')
def sexec(argv):
  es.sexec(*argv)

@Command(syntax='<commandstring>', desc='Forces all users to execute a command on the server console.')
def sexec_all(argv):
  es.sexec_all(*argv)

@Command(syntax='<userid> <x> <y> [z]', desc='Teleports a player.')
def setpos(argv):
  es.setpost(*argv)

@Command(syntax='<userid> <pitch> <yaw> [roll]', desc='Sets player view angle.')
def setang(argv):
  es.setang(*argv)

@Command(syntax='<userid> <teamnum>', desc='Changes the team of the player.')
def changeteam(argv):
  es.changeteam(*argv)

@Command(syntax='<userid> [entity-index]', desc='Adds a console command that refers to a particular block.')
def setview(argv):
  es.setview(*argv)

@Command(syntax='<userid>', desc='Spawn a player with the given userid.')
def spawnplayer(argv):
  es.spawnplayer(*argv)
