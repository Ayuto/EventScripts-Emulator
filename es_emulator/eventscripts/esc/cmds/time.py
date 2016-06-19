from . import Command
import es

@Command(syntax='<varname>', desc='Stores the server time in a variable.')
def gettime(addonref, argv):
  raise NotImplementedError

@Command(syntax='<varname>', desc='Stores a timestamp in seconds in a variable. gettimestamp provides a shorter timestamp only for comparing against other es_gettimestamp values.')
def gettimestamp(addonref, argv):
  raise NotImplementedError
  
@Command(syntax='<varname>', desc='Stores the server time string in a variable.')
def gettimestring(addonref, argv):
  raise NotImplementedError
