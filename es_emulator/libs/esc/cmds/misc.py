from . import Command

@Command(con=True, desc='Update an entry in a stringtable')
def stringtable(argv):
  pass

@Command(con=True, desc='Update an entry in a stringtable')
def dumpstringtable(argv):
  pass
  
@Command(con=True, desc='Local database support')
def sql(argv, args):
  pass

@Command(con=True, desc='Does some SQL.')
def dosql(argv):
  pass
  
@Command(con=True, desc='Reads an event file and registers EventScripts as a handler for those events.')
def loadevents(argv):
  pass

@Command(con=True, desc='Runs an exec file from memory.')
def mexec(argv):
  pass

@Command(con=True, desc='Adds a bot to the server.')
def createbot(argv):
  pass

@Command(con=True, desc='Performs a particular effect.')
def effect(argv):
  pass

@Command(con=True, desc='Create and fire events to signal to plugins that an event has happened. It must be an event loaded via es_loadevents.')
def event(argv):
  pass
