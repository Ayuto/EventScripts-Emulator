from . import Command

@Command(con=True, desc='Allows you to control listening players.')
def voicechat(argv):
  pass

@Command(con=True, desc='Forces a userid to execute a command in their console.')
def cexec(argv):
  pass
  
@Command(con=True, desc='Forces a userid to execute a command on the server console (bypassing client console).')
def sexec(argv):
  pass
  
@Command(con=True, desc='Teleports a player.')
def setpos(argv):
  pass

@Command(con=True, desc='Sets player view angle.')
def setang(argv):
  pass
  
@Command(con=True, desc='Changes the team of the player.')
def changeteam(argv):
  pass

@Command(con=True, desc='Adds a console command that refers to a particular block.')
def setview(argv):
  pass
