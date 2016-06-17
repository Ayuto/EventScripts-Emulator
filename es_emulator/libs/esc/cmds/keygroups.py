import es
from keyvalues import getKeyGroup
from .. import stack
from ..parse import getcode
from . import Command

@Command(con=True, desc='Creates a keygroup that can be loaded and saved to a file. Must call es_keygroupdelete to free this memory!')
def keygroupcreate(argv):
  pass

@Command(con=True, desc='Deletes a keygroup from memory so that it\'s not leaked.')
def keygroupdelete(argv):
  pass

@Command(con=True, desc='Renames an existing keygroup.')
def keygrouprename(argv):
  pass
  
@Command(con=True, desc='Lists all key values in memory that aren\'t groups. Optionally can look up a group, if you provide one.')
def keylist(argv):
  pass

@Command(con=True, desc='Copies a keygroup.')
def keygroupcopy(argv):
  pass

@Command(con=True, desc='Loads a keygroup from file based on its name.')
def keygroupload(argv):
  pass

@Command(con=True, desc='Saves a keygroup to a file based on its name.')
def keygroupsave(argv):
  pass

@Command(con=True, desc='Creates a key that can be free-floating or associated with a group. Must call es_keydelete to free this memory when you\'re done.')
def keycreate(argv):
  pass

@Command(con=True, desc='Deletes a key from memory so that it\'s not leaked when you\'re done with it.')
def keydelete(argv):
  pass

@Command(con=True, desc='Deletes keys from a keygroup that match or don\'t match a certain value.')
def keygroupfilter(argv):
  pass

@Command(con=True, desc='Rename a key.')
def keyrename(argv):
  pass

@Command(con=True, desc='Sets a value within a given key (where the key could be free-floating or associated with a group).')
def keysetvalue(argv):
  pass

@Command(con=True, desc='Gets a value within a given key (where the key could be free-floating or associated with a group).')
def keygetvalue(argv):
  pass
  
@Command(syntax='<var> in <groupname> <keyname> <command>', desc='EXPERIMENTAL. Loops through a keygroup and performs a single command on each key, providing a single variable with the key name.')
def foreachval(argv):
  var, isin, keygroup, key, commands = argv[:5]
  if isin != 'in':
    raise SyntaxError
  if not es.exists('keygroup', keygroup):
    raise NameError, ('keygroup', keygroup)
  if not es.exists('key', keygroup, key):
    raise NameError, ('key', '%s/%s' % (keygroup, key))
  stack.setfor(var, getKeyGroup(keygroup)[key].keys())
  stack.insertrawblock(commands)

@Command(syntax='<var> in <groupname> <command>', desc='EXPERIMENTAL. Loops through a keygroup and performs a single command on each key, providing a single variable with the key name.')
def foreachkey(argv):
  var, isin, keygroup, commands = argv[:4]
  if isin != 'in':
    raise SyntaxError
  if not es.exists('keygroup', keygroup):
    raise NameError, ('keygroup', keygroup)
  stack.setfor(var, getKeyGroup(keygroup).keys())
  stack.insertrawblock(commands)
