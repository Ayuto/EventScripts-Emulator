# ./addons/eventscripts/corelib/keyrand/keyrand.py
# ported to Python by Hunter

import es
import cmdlib

import random
import keyvalues

def load():
    cmdlib.registerServerCommand('keyrand', keyrand_cmd, 'Syntax: keyrand <variable> <keygroup> [key]')

    for line in (
        'testcase qcreate corelib keyrandtest "Tests keyrand"',
        'testcase addtest keyrandtest keyrandtest corelib/keyrand/testcase "Keyrand Corelib Command Test"'):
        es.server.queuecmd(line)

def unload():
    cmdlib.unregisterServerCommand('keyrand')

def keyrand_cmd(args):
    if len(args) > 1:
        keygroup = args[1]
        if es.exists('keygroup', keygroup):
            kv = keyvalues.getKeyGroup(keygroup)
            if not len(args) > 2:
                es.ServerVar(args[0]).set(str(random.choice(kv.keys())))
            elif es.exists('key', keygroup, args[2]):
                es.ServerVar(args[0]).set(str(random.choice(kv[args[2]].keys())))
            else:
                es.dbgmsg(0, 'keyrand: Invalid key for keygroup "%s" provided: %s' % (keygroup, args[2]))
        else:
            es.dbgmsg(0, 'keyrand: Invalid keygroup provided: %s' % keygroup)
    else:
        es.dbgmsg(0, 'keyrand: Not enough arguments to keyrand. Syntax: keyrand <variable> <keygroup> [key]')

def testcase():
    for line in (
        'es_xkeygroupcreate _keyrand',
        'es_xkeycreate _keyrand 1',
        'es_xkeycreate _keyrand 2',
        'es_xkeycreate _keyrand 3',
        'es_xkeysetvalue _keyrand 1 1 blah',
        'es_xkeysetvalue _keyrand 1 2 blah',
        'es_xkeysetvalue _keyrand 1 3 blah',
        'es_xkeysetvalue _keyrand 1 4 blah',
        'es_xkeysetvalue _keyrand 2 1 blah',
        'es_xkeysetvalue _keyrand 2 2 blah',
        'es_xkeysetvalue _keyrand 3 1 blah',
        'es_xkeysetvalue _keyrand 3 2 blah',
        'profile begin keyrand_test',
        'profile begin keyrand_key',
        'testlib begin keyrand_key "keyrand key"',
        'es_xset _keyrand_testvar 0',
        'keyrand _keyrand_testvar _keyrand',
        'es_keygetvalue _keyrand_testvar _keyrand server_var(_keyrand_testvar) 1',
        'testlib fail_unless _keyrand_testvar equalto blah',
        'testlib end',
        'profile end keyrand_key',
        'profile begin keyrand_keyvar',
        'testlib begin keyrand_keyvar "keyrand keyvar"',
        'es_xset _keyrand_testvar 0',
        'keyrand _keyrand_testvar _keyrand 1',
        'es_keygetvalue _keyrand_testvar _keyrand 1 server_var(_keyrand_testvar)',
        'testlib fail_unless _keyrand_testvar equalto blah',
        'testlib end',
        'profile end keyrand_keyvar',
        'profile end keyrand_test',
        'es_xkeygroupdelete _keyrand'):
        es.server.cmd(line)
