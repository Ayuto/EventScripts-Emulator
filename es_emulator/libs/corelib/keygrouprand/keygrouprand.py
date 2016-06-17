# ./addons/eventscripts/corelib/keygrouprand/keygrouprand.py
# ported to Python by Hunter

import es
import cmdlib

import random
import keyvalues

def load():
    cmdlib.registerServerCommand('keygrouprand', keygrouprand_cmd, 'Syntax: keygrouprand <keygroup> [#key/#keyvalue/#all] [keylimit]')

def unload():
    cmdlib.unregisterServerCommand('keygrouprand')

def keygrouprand_cmd(args):
    if len(args) > 0:
        keygroup = args[0]
        if es.exists('keygroup', keygroup):
            if len(args) > 1:
                target = args[1]
            else:
                target = '#all'
            if target in ['#key', '#keyvalue', '#all']:
                dc = {}
                kv = keyvalues.getKeyGroup(keygroup)
                if len(args) > 2 and args[2].isdigit():
                    keylimit = int(args[2])
                else:
                    keylimit = len(kv.keys())
                for key in kv.keys():
                    dc[key] = {}
                    for keyvalue in kv[key].keys():
                        dc[key][keyvalue] = kv[key][keyvalue]
                if target == '#all' or target == '#key':
                    keylist = random.sample(dc.keys(), keylimit)
                else:
                    keylist = dc.keys()[:keylimit]
                # Let's re-create our keygroup with classic ES commands 
                es.keygroupdelete(keygroup)
                es.keygroupcreate(keygroup)
                for key in keylist:
                    es.keycreate(keygroup, key)
                    if target == '#all' or target == '#keyvalue':
                        for keyvalue in random.sample(dc[key].keys(), len(dc[key])):
                            es.keysetvalue(keygroup, key, keyvalue, dc[key][keyvalue])
                    else:
                        for keyvalue in dc[key].keys():
                            es.keysetvalue(keygroup, key, keyvalue, dc[key][keyvalue])
            else:
                es.dbgmsg(0, 'keygrouprand: Invalid target provided: %s' % target)
        else:
            es.dbgmsg(0, 'keygrouprand: Invalid keygroup provided: %s' % keygroup)
    else:
        es.dbgmsg(0, 'keygrouprand: Not enough arguments to keygrouprand. Syntax: keygrouprand <keygroup> [#key/#keyvalue/#all] [keylimit]')
