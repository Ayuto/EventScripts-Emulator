# ./addons/eventscripts/corelib/keygroupsort/keygroupsort.py
# ported to Python by Hunter
# original command by Don and XE_ManUp

import es
import cmdlib

import keyvalues

def load():
    cmdlib.registerServerCommand('keygroupsort', keygroupsort_cmd, 'Syntax: keygroupsort <keygroup> <field to sort> [<des/asc #numeric/#alpha>]')

def unload():
    cmdlib.unregisterServerCommand('keygroupsort')

def keygroupsort_cmd(args):
    if len(args) > 1:
        keygroup = args[0]
        if es.exists('keygroup', keygroup):
            dc = {}
            kv = keyvalues.getKeyGroup(keygroup)
            sortfield = args[1]
            if es.exists('keyvalue', keygroup, kv.keys()[0], sortfield) or keygroup == sortfield:
                if len(args) > 3:
                    sortorder = 'asc' if args[2].lower() == 'asc' else 'des'
                    sorttype = '#alpha' if args[3].lower() == '#alpha' else '#numeric'
                else:
                    sortorder = 'des'
                    sorttype = '#numeric'
                for key in kv.keys():
                    dc[key] = {}
                    for keyvalue in kv[key].keys():
                        dc[key][keyvalue] = kv[key][keyvalue]
                if keygroup == sortfield:
                    if sortorder == 'asc' and sorttype == '#alpha':
                        keylist = sorted(dc.keys())
                    elif sortorder == 'des' and sorttype == '#alpha':
                        keylist = sorted(dc.keys(), reverse=True)
                    elif sortorder == 'asc' and sorttype == '#numeric':
                        keylist = sorted(dc.keys(), key=lambda x: int(x) if str(x).isdigit() else x)
                    else:
                        keylist = sorted(dc.keys(), key=lambda x: int(x) if str(x).isdigit() else x, reverse=True)
                else:
                    if sortorder == 'asc' and sorttype == '#alpha':
                        keylist = map(lambda x: x[0], sorted(dc.items(), key=lambda x: x[1][sortfield]))
                    elif sortorder == 'des' and sorttype == '#alpha':
                        keylist = map(lambda x: x[0], sorted(dc.items(), key=lambda x: x[1][sortfield], reverse=True))
                    elif sortorder == 'asc' and sorttype == '#numeric':
                        keylist = map(lambda x: x[0], sorted(dc.items(), key=lambda x: int(x[1][sortfield]) if str(x[1][sortfield]).isdigit() else x[1][sortfield]))
                    else:
                        keylist = map(lambda x: x[0], sorted(dc.items(), key=lambda x: int(x[1][sortfield]) if str(x[1][sortfield]).isdigit() else x[1][sortfield], reverse=True))
                # Let's re-create our keygroup with classic ES commands 
                es.keygroupdelete(keygroup)
                es.keygroupcreate(keygroup)
                for key in keylist:
                    es.keycreate(keygroup, key)
                    for keyvalue in dc[key].keys():
                        es.keysetvalue(keygroup, key, keyvalue, dc[key][keyvalue])
            else:
                es.dbgmsg(0, 'keygroupsort: Invalid field to sort provided: %s' % sortfield)
        else:
            es.dbgmsg(0, 'keygroupsort: Invalid keygroup provided: %s' % keygroup)
    else:
        es.dbgmsg(0, 'keygroupsort: Not enough arguments to keygroupsort. Syntax: keygroupsort <keygroup> <field to sort> [<des/asc #numeric/#alpha>]')
