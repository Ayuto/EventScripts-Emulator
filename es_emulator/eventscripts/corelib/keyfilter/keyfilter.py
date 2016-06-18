# ./addons/eventscripts/corelib/keyfilter/keyfilter.py
# ported to Python by Hunter

import es
import cmdlib

import keyvalues

def load():
    cmdlib.registerServerCommand('keyfilter', keyfilter_cmd, 'Syntax: keyfilter <keygroup> <key> <not/only> <part-of-value-name> [value]')

    for line in (
        'testcase qcreate corelib keyfiltertest "Tests keyfilter"',
        'testcase addtest keyfiltertest keyfiltertest corelib/keyfilter/testcase "Keyfilter Corelib Command Test"'):
        es.server.queuecmd(line)

def unload():
    cmdlib.unregisterServerCommand('keyfilter')

def keyfilter_cmd(args):
    if len(args) > 3:
        keygroup = args[0]
        if es.exists('keygroup', keygroup):
            key = args[1]
            if es.exists('key', keygroup, key):
                action = args[2]
                if action in ['not', 'only']:
                    kv = keyvalues.getKeyGroup(keygroup)
                    keyfiltervar = args[3]
                    keyfilterlist = []
                    if len(args) > 4:
                        keyfiltervalue = args[4]
                    else:
                        keyfiltervalue = None
                    if action == 'not':
                        for keyvar in kv[key].keys():
                            if keyfiltervar in keyvar and (str(kv[key][keyvar]) == keyfiltervalue or not keyfiltervalue):
                                keyfilterlist.append(keyvar)
                    elif action == 'only':
                        for keyvar in kv[key].keys():
                            if not keyfiltervar in keyvar or (str(kv[key][keyvar]) != keyfiltervalue and keyfiltervalue):
                                keyfilterlist.append(keyvar)
                    for keyvar in keyfilterlist:
                        if keyvar in kv[key]:
                            del kv[key][keyvar]
                else:
                    es.dbgmsg(0, 'keyfilter: Invalid action provided. Syntax: keyfilter <keygroup> <key> <not/only> <part-of-value-name> [value]')
            else:
                es.dbgmsg(0, 'keyfilter: Invalid key for keygroup "%s" provided: %s' % (keygroup, key))
        else:
            es.dbgmsg(0, 'keyfilter: Invalid keygroup provided: %s' % keygroup)
    else:
        es.dbgmsg(0, 'keyfilter: Not enough arguments to keyfilter. Syntax: <keygroup> <key> <not/only> <part-of-value-name> [value]')

def testcase():
    for line in (
        'es_xkeygroupcreate _keyfilter',
        'es_xkeycreate _keyfilter _keyfilterkey',
        'es_xkeysetvalue _keyfilter _keyfilterkey val1 deleteme',
        'es_xkeysetvalue _keyfilter _keyfilterkey val2 deleteme',
        'es_xkeysetvalue _keyfilter _keyfilterkey val3 keepme',
        'es_xkeysetvalue _keyfilter _keyfilterkey val4 keepme',
        'es_xkeysetvalue _keyfilter _keyfilterkey abc1 test',
        'es_xkeysetvalue _keyfilter _keyfilterkey abc2 test',
        'es_xkeysetvalue _keyfilter _keyfilterkey cba3 test',
        'es_xkeysetvalue _keyfilter _keyfilterkey cba4 test',
        'profile begin keyfilter_test',
        'profile begin keyfilter_not',
        'testlib begin keyfilter_not "keyfilter not value"',
        'es_xset _keyfilter_testvar 0',
        'keyfilter _keyfilter _keyfilterkey not val deleteme',
        'es_xexists _keyfilter_testvar keyvalue _keyfilter _keyfilterkey val1',
        'testlib fail_unless _keyfilter_testvar equalto 0',
        'es_xexists _keyfilter_testvar keyvalue _keyfilter _keyfilterkey val2',
        'testlib fail_unless _keyfilter_testvar equalto 0',
        'es_xexists _keyfilter_testvar keyvalue _keyfilter _keyfilterkey val3',
        'testlib fail_unless _keyfilter_testvar equalto 1',
        'es_xexists _keyfilter_testvar keyvalue _keyfilter _keyfilterkey val4',
        'testlib fail_unless _keyfilter_testvar equalto 1',
        'testlib end',
        'profile end keyfilter_not',
        'es_xkeysetvalue _keyfilter _keyfilterkey val1 deleteme',
        'es_xkeysetvalue _keyfilter _keyfilterkey val2 deleteme',
        'es_xkeysetvalue _keyfilter _keyfilterkey val3 keepme',
        'es_xkeysetvalue _keyfilter _keyfilterkey val4 keepme',
        'es_xkeysetvalue _keyfilter _keyfilterkey abc1 test',
        'es_xkeysetvalue _keyfilter _keyfilterkey abc2 test',
        'es_xkeysetvalue _keyfilter _keyfilterkey cba3 test',
        'es_xkeysetvalue _keyfilter _keyfilterkey cba4 test',
        'profile begin keyfilter_only',
        'testlib begin keyfilter_only "keyfilter only value"',
        'es_xset _keyfilter_testvar 0',
        'keyfilter _keyfilter _keyfilterkey only val keepme',
        'es_xexists _keyfilter_testvar keyvalue _keyfilter _keyfilterkey val1',
        'testlib fail_unless _keyfilter_testvar equalto 0',
        'es_xexists _keyfilter_testvar keyvalue _keyfilter _keyfilterkey val1',
        'testlib fail_unless _keyfilter_testvar equalto 0',
        'es_xexists _keyfilter_testvar keyvalue _keyfilter _keyfilterkey val3',
        'testlib fail_unless _keyfilter_testvar equalto 1',
        'es_xexists _keyfilter_testvar keyvalue _keyfilter _keyfilterkey val4',
        'testlib fail_unless _keyfilter_testvar equalto 1',
        'testlib end',
        'profile end keyfilter_only',
        'es_xkeysetvalue _keyfilter _keyfilterkey val1 deleteme',
        'es_xkeysetvalue _keyfilter _keyfilterkey val2 deleteme',
        'es_xkeysetvalue _keyfilter _keyfilterkey val3 keepme',
        'es_xkeysetvalue _keyfilter _keyfilterkey val4 keepme',
        'es_xkeysetvalue _keyfilter _keyfilterkey abc1 test',
        'es_xkeysetvalue _keyfilter _keyfilterkey abc2 test',
        'es_xkeysetvalue _keyfilter _keyfilterkey cba3 test',
        'es_xkeysetvalue _keyfilter _keyfilterkey cba4 test',
        'profile begin keyfilter_not',
        'testlib begin keyfilter_not "keyfilter not"',
        'es_xset _keyfilter_testvar 0',
        'keyfilter _keyfilter _keyfilterkey not abc',
        'es_xexists _keyfilter_testvar keyvalue _keyfilter _keyfilterkey abc1',
        'testlib fail_unless _keyfilter_testvar equalto 0',
        'es_xexists _keyfilter_testvar keyvalue _keyfilter _keyfilterkey abc2',
        'testlib fail_unless _keyfilter_testvar equalto 0',
        'es_xexists _keyfilter_testvar keyvalue _keyfilter _keyfilterkey cba3',
        'testlib fail_unless _keyfilter_testvar equalto 1',
        'es_xexists _keyfilter_testvar keyvalue _keyfilter _keyfilterkey cba4',
        'testlib fail_unless _keyfilter_testvar equalto 1',
        'testlib end',
        'profile end keyfilter_not',
        'es_xkeysetvalue _keyfilter _keyfilterkey val1 deleteme',
        'es_xkeysetvalue _keyfilter _keyfilterkey val2 deleteme',
        'es_xkeysetvalue _keyfilter _keyfilterkey val3 keepme',
        'es_xkeysetvalue _keyfilter _keyfilterkey val4 keepme',
        'es_xkeysetvalue _keyfilter _keyfilterkey abc1 test',
        'es_xkeysetvalue _keyfilter _keyfilterkey abc2 test',
        'es_xkeysetvalue _keyfilter _keyfilterkey cba3 test',
        'es_xkeysetvalue _keyfilter _keyfilterkey cba4 test',
        'profile begin keyfilter_only',
        'testlib begin keyfilter_only "keyfilter only"',
        'es_xset _keyfilter_testvar 0',
        'keyfilter _keyfilter _keyfilterkey only cba',
        'es_xexists _keyfilter_testvar keyvalue _keyfilter _keyfilterkey abc1',
        'testlib fail_unless _keyfilter_testvar equalto 0',
        'es_xexists _keyfilter_testvar keyvalue _keyfilter _keyfilterkey abc2',
        'testlib fail_unless _keyfilter_testvar equalto 0',
        'es_xexists _keyfilter_testvar keyvalue _keyfilter _keyfilterkey cba3',
        'testlib fail_unless _keyfilter_testvar equalto 1',
        'es_xexists _keyfilter_testvar keyvalue _keyfilter _keyfilterkey cba4',
        'testlib fail_unless _keyfilter_testvar equalto 1',
        'testlib end',
        'profile end keyfilter_only',
        'profile end keyfilter_test',
        'es_xkeygroupdelete _keyfilter'):
        es.server.cmd(line)
