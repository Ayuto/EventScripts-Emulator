import es
from keyvalues import getKeyGroup
from .. import stack
from ..parse import getcode
from . import Command

from es_C import user_groups

@Command(syntax='<groupname>', desc='Creates a keygroup that can be loaded and saved to a file. Must call es_keygroupdelete to free this memory!')
def keygroupcreate(argv):
  es.keygroupcreate(*argv)

@Command(syntax='<groupname>', desc='Deletes a keygroup from memory so that it\'s not leaked.')
def keygroupdelete(argv):
  es.keygroupdelete(*argv)

@Command(syntax='<groupname> <newname>', desc='Renames an existing keygroup.')
def keygrouprename(argv):
  es.keygrouprename(*argv)

@Command(syntax='[group]', desc='Lists all key values in memory that aren\'t groups. Optionally can look up a group, if you provide one.')
def keylist(argv):
  es.keylist(*argv)

@Command(syntax='<FromKeygroup> <ToKeygroup>', desc='Copies a keygroup.')
def keygroupcopy(argv):
  es.keygroupcopy(*argv)

@Command(syntax='<groupname> [path]', desc='Loads a keygroup from file based on its name.')
def keygroupload(argv):
  es.keygroupload(*argv)

@Command(syntax='<groupname> [path]', desc='Saves a keygroup to a file based on its name.')
def keygroupsave(argv):
  es.keygroupsave(*argv)

@Command(syntax='[group] <key>', desc='Creates a key that can be free-floating or associated with a group. Must call es_keydelete to free this memory when you\'re done.')
def keycreate(argv):
  es.keycreate(*argv)

@Command(syntax='[group] <key>', desc='Deletes a key from memory so that it\'s not leaked when you\'re done with it.')
def keydelete(argv):
  es.keydelete(*argv)

@Command(syntax='[group] <not/only> <value-name> <value>', desc='Deletes keys from a keygroup that match or don\'t match a certain value.')
def keygroupfilter(argv):
  es.keygroupfilter(*argv)

@Command(syntax='[group] <key> <newkeyname>', desc='Rename a key.')
def keyrename(argv):
  es.keyrename(*argv)

@Command(syntax='[group] <key> <valuename> <value>', desc='Sets a value within a given key (where the key could be free-floating or associated with a group).')
def keysetvalue(argv):
  es.keysetvalue(*argv)

@Command(syntax='<var> [group] <key> <valuename>', desc='Gets a value within a given key (where the key could be free-floating or associated with a group).')
def keygetvalue(argv):
  es.keygetvalue(*argv)

@Command(pre=False, desc='Lists all in-memory keygroups.')
def es_keygrouplist(argv):
  es.dbgmsg(0, '----------------------')
  key = user_groups.first_true_sub_key
  while key:
    es.dbgmsg(0, 'Key: {}'.format(key.name))
    value = key.first_value
    while value:
        es.dbgmsg(0, '   Name: {}\n  Value: {}'.format(value.name, value.get_string()))
        value = value.next_value
        
    key = key.next_true_sub_key
  es.dbgmsg(0, '----------------------')

@Command(syntax='<var> in <groupname> <keyname> <command>', desc='EXPERIMENTAL. Loops through a keygroup and performs a single command on each key, providing a single variable with the key name.')
def foreachval(argv):
  var, isin, keygroup, key, commands = argv[:5]
  if isin != 'in':
    raise SyntaxError
  if not es.exists('keygroup', keygroup):
    raise NameError('keygroup', keygroup)
  if not es.exists('key', keygroup, key):
    raise NameError('key', '%s/%s' % (keygroup, key))
  stack.setfor(var, list(getKeyGroup(keygroup)[key].keys()))
  stack.insertrawblock(commands)

@Command(syntax='<var> in <groupname> <command>', desc='EXPERIMENTAL. Loops through a keygroup and performs a single command on each key, providing a single variable with the key name.')
def foreachkey(argv):
  var, isin, keygroup, commands = argv[:4]
  if isin != 'in':
    raise SyntaxError
  if not es.exists('keygroup', keygroup):
    raise NameError('keygroup', keygroup)
  stack.setfor(var, list(getKeyGroup(keygroup).keys()))
  stack.insertrawblock(commands)
