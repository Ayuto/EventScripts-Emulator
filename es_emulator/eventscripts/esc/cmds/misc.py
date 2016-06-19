from . import Command
import es

@Command(syntax='<tablename> <string>', desc='Update an entry in a stringtable')
def stringtable(argv):
  es.stringtable(*argv)

@Command(syntax='<tablename> <string>', desc='Update an entry in a stringtable')
def dumpstringtable(argv):
  es.dumpstringtable(*argv)
  
# es_xsql open <db> [dbdir]
# es_xsql close <db>
# es_xsql queryvalue <db> <single-result-var> "<SQL-string>"
# es_xsql query <db> [result-keygroup] "<SQL-string>"
@Command(syntax='<operation> <db> [var] [sql]', desc='Local database support')
def sql(argv, args):
  es.sql(*sql)

@Command(syntax='<db> <query>', desc='Does some SQL.')
def dosql(argv):
  es.dosql(*argv)
  
@Command(syntax='[declare] <pathtoeventfile>', desc='Reads an event file and registers EventScripts as a handler for those events.')
def loadevents(argv):
  es.loadevents(*argv)

@Command(syntax='<path/script>', desc='Runs an exec file from memory.')
def mexec(argv):
  es.mexec(*argv)

@Command(syntax='[var] <botname>', desc='Adds a bot to the server.')
def createbot(argv):
  es.createbot(*argv)

@Command(syntax='<mode> [options]', desc='Performs a particular effect.')
def effect(argv):
  es.effect(*argv)

@Command(syntax='<command> <event-name> [value-name] [value]', desc='Create and fire events to signal to plugins that an event has happened. It must be an event loaded via es_loadevents.')
def event(argv):
  es.event(*argv)
