# ./addons/eventscripts/keymenu/keymenu.py
# ported to Python by Hunter

#keymenu create <name> <return var> <script/block> <keygroup> <menu display> <menu return> Menu Title Text
#keymenu delete <name>
#keymenu send <name> <userid> [page]
#keymenu unsend <name> <users> [page]
#keymenu getpages <var> <name>
#keymenu exists <var> <name>
#keymenu changeblock <name> <script/block>
#keymenu setvar <name> <menu var> <menu value>
#keymenu getvar <name> <var> <menu var>
#keymenu backmenu <name> <keymenu/popup>
#keymenu getmenuname <var> <popup-name>
#keymenu update <name> [keygroup]

import es
import cmdlib

import playerlib
import keymenulib

def load():
    cmdlib.registerServerCommand('keymenu', keymenu_cmd, 'Keymenu console command')

def unload():
    cmdlib.unregisterServerCommand('keymenu')

def keymenu_cmd(args):
    if len(args):
        subcmd = args[0].lower()
        if len(args) > 1:
            kname = args[1]
        else:
            kname = ''
        if len(kname) and keymenulib.exists(kname):
            k = keymenulib.find(kname)
        else:
            k = None
        if subcmd == 'create':
            if len(args) > 6:
                index = 5
                titletext = ''
                if args[index] == '#key':
                    menudisplay = args[index]
                    index += 1
                elif args[index] == '#keyvalue':
                    menudisplay = args[index] + ' ' + args[index+1]
                    index += 2
                if args[index] == '#key':
                    menureturn = args[index]
                    index += 1
                elif args[index] == '#keyvalue':
                    menureturn = args[index] + ' ' + args[index+1]
                    index += 2
                for subindex in range(index, len(args)):
                    titletext += args[subindex] + ' '
                keymenulib.create(kname, args[2], args[3], args[4], menudisplay, menureturn, titletext.rstrip())
            else:
                es.dbgmsg(0, 'Syntax: keymenu create <name> <return var> <script/block> <keygroup> <menu display> <menu return> Menu Title Text')
        elif subcmd == 'delete':
            if kname and len(args) > 1:
                if k:
                    keymenulib.delete(kname)
                else:
                    es.dbgmsg(0, 'keymenu delete: No such keymenu: %s' % kname)
            else:
                es.dbgmsg(0, 'Syntax: keymenu delete <name>')
        elif subcmd == 'send':
            if kname and len(args) > 2:
                if k:
                    if '#' in args[2]:
                        args[2] = args[2].replace('#', ',#')[1:]
                    if len(args) > 3 and args[3].isdigit():
                        k.send(playerlib.getUseridList(args[2]), int(args[3]))
                    else:
                        k.send(playerlib.getUseridList(args[2]))
                else:
                    es.dbgmsg(0, 'keymenu send: No such keymenu: %s' % kname)
            else:
                es.dbgmsg(0, 'Syntax: keymenu send <name> <users> [page]')
        elif subcmd == 'unsend':
            if kname and len(args) > 2:
                if k:
                    if '#' in args[2]:
                        args[2] = args[2].replace('#', ',#')[1:]
                    if len(args) > 3 and args[3].isdigit():
                        k.unsend(playerlib.getUseridList(args[2]), int(args[3]))
                    else:
                        k.unsend(playerlib.getUseridList(args[2]))
                else:
                    es.dbgmsg(0, 'keymenu unsend: No such keymenu: %s' % kname)
            else:
                es.dbgmsg(0, 'Syntax: keymenu unsend <name> <users> [page]')
        elif subcmd == 'update':
            if kname and len(args) > 1:
                if k:
                    if len(args) > 2:
                        if es.exists('keygroup', args[2]):
                            k.update(args[2])
                        else:
                            es.dbgmsg(0, 'keymenu update: No such keygroup: %s' % args[2])
                    else:
                        k.update()
                else:
                    es.dbgmsg(0, 'keymenu update: No such keymenu: %s' % kname)
            else:
                es.dbgmsg(0, 'Syntax: keymenu update <name> [keygroup]')
        elif subcmd == 'exists':
            if len(args) > 2:
                es.ServerVar(args[1]).set(int(keymenulib.exists(args[2])))
            else:
                es.dbgmsg(0, 'Syntax: keymenu exists <var> <name>')
        elif subcmd == 'getpages':
            if len(args) > 2:
                if keymenulib.exists(args[2]):
                    es.ServerVar(args[1]).set(int(keymenulib.find(args[2]).getpages()))
                else:
                    es.dbgmsg(0, 'keymenu getpages: No such keymenu: %s' % args[2])
            else:
                es.dbgmsg(0, 'Syntax: keymenu getpages <var> <name>')
        elif subcmd == 'getmenuname':
            if len(args) > 2:
                if popuplib.exists(args[2]):
                    es.ServerVar(args[1]).set(str(keymenulib.getmenuname(args[2])))
                else:
                    es.dbgmsg(0, 'keymenu getmenuname: No such popup: %s' % args[2])
            else:
                es.dbgmsg(0, 'Syntax: keymenu getmenuname <var> <popup-name>')
        elif subcmd == 'changeblock':
            if len(args) > 2:
                if k:
                    k.changeblock(args[2])
                else:
                    es.dbgmsg(0, 'keymenu changeblock: No such keymenu: %s' % kname)
            else:
                es.dbgmsg(0, 'Syntax: keymenu changeblock <name> <script/block>')
        elif subcmd == 'backmenu':
            if len(args) > 2:
                if k:
                    k.backmenu(args[2])
                else:
                    es.dbgmsg(0, 'keymenu backmenu: No such keymenu: %s' % kname)
            else:
                es.dbgmsg(0, 'Syntax: keymenu backmenu <name> <keymenu/popup>')
        elif subcmd == 'setvar':
            if len(args) > 3:
                if k:
                    if args[2].isalnum():
                        setattr(k, args[2], args[3])
                    else:
                        es.dbgmsg(0, 'keymenu setvar: Invalid keymenu variable name')
                else:
                    es.dbgmsg(0, 'keymenu setvar: No such keymenu: %s' % kname)
            else:
                es.dbgmsg(0, 'Syntax: keymenu setvar <name> <variable> <value>')
        elif subcmd == 'getvar':
            if len(args) > 4:
                if k:
                    if args[3].isalnum() and hasattr(k, args[3]):
                        es.ServerVar(args[2]).set(getattr(k, args[3]))
                    else:
                        es.dbgmsg(0, 'keymenu getvar: Invalid keymenu variable name')
                else:
                    es.dbgmsg(0, 'keymenu getvar: No such keymenu: %s' % kname)
            else:
                es.dbgmsg(0, 'Syntax: keymenu getvar <name> <var> <variable>')
        elif subcmd == 'list':
            if len(args) > 1:
                listlevel = int(kname)
            else:
                listlevel = 0
            for kname in keymenulib.getmenulist():
                keymenulib.find(kname).information(listlevel)
            if not len(args) > 1:
                es.dbgmsg(0, ' ')
                es.dbgmsg(0, 'For more details, supply list level (0-1):')
                es.dbgmsg(0, 'Syntax: keymenu list [level]')
        elif subcmd == 'info':
            if k:
                k.information(listlevel, 1)
            else:
                es.dbgmsg(0, 'keymenu info: No such keymenu: %s' % kname)
            if not len(args) > 1:
                es.dbgmsg(0, ' ')
                es.dbgmsg(0, 'Syntax: keymenu info <name>')
        else:
            es.dbgmsg(0, 'Invalid keymenu subcommand, see http://www.eventscripts.com/pages/Keymenu/ for a list of subcommands')
    else:
        es.dbgmsg(0, 'Missing keymenu subcommand, see http://www.eventscripts.com/pages/Keymenu/ for a list of subcommands')
