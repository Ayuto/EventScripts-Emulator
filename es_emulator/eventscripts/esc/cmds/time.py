from . import Command
from ..val import sv, VAR
import es
import time

@Command(syntax='<varname>', types=VAR, desc='Stores the server time in a variable.')
def gettime(argv):
  sv[argv[0]] = int(time.time())

@Command(syntax='<varname>', types=VAR, desc='Stores a timestamp in seconds in a variable. gettimestamp provides a shorter timestamp only for comparing against other es_gettimestamp values.')
def gettimestamp(argv):
  sv[argv[0]] = int(time.time() - 1136049334)

@Command(syntax='<varname>', types=VAR, desc='Stores the server time string in a variable.')
def gettimestring(argv):
  sv[argv[0]] = time.strftime(es.getString('eventscripts_timeformat'))
