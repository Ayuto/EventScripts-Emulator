# ./addons/eventscripts/corelib/usermsglib/usermsglib.py
# Backwards compatibility with non Python versions of ES

import es
import cmdlib

import usermsg

def load():
    cmdlib.registerServerCommand('usermsg', usermsg_cmd, 'Corelib command: usermsg used as a shortcut for es_usermsg')

def unload():
    cmdlib.unregisterServerCommand('usermsg')

def usermsg_cmd(args):
    if len(args) == 1:
        if args[0] == 'list':
            es.dbgmsg(0, "usermsg fade: Syntax: fade <userid> <0 = no fade, 1 = fade Out 2 = fade in> <time to fade (in frames)> <time faded (in frames)> <red> <green> <blue> <alpha>")
            es.dbgmsg(0, "usermsg shake: Syntax: shake <userid> <magnitude> <time>")
            es.dbgmsg(0, "usermsg motd: Syntax: motd <userid> <0 = text, 2 = url> <title> <msg>")
            es.dbgmsg(0, "usermsg hudhint: Syntax: hudhint <userid> <msg>")
            es.dbgmsg(0, "usermsg keyhint: Syntax: keyhint <userid> <msg>")
            es.dbgmsg(0, "usermsg centermsg: Syntax: centermsg <userid> <msg>")
        else:
            es.dbgmsg(0, 'usermsg: Invalid parameters, type "usermsg list" to see a list of valid subcommands')
    elif len(args) > 1:
        subcommand = args[0]
        if subcommand == 'fade':
            if len(args) > 8:
              usermsg.fade(args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8])
            else:
              es.dbgmsg(0, "usermsg fade: Syntax: fade <userid> <0 = no fade, 1 = fade Out 2 = fade in> <time to fade (in frames)> <time faded (in frames)> <red> <green> <blue> <alpha>")
        elif subcommand == 'shake':
            if len(args) > 3:
              usermsg.shake(args[1], args[2], args[3])
            else:
              es.dbgmsg(0, "usermsg shake: Syntax: shake <userid> <magnitude> <time>")
        elif subcommand == 'motd':
            if len(args) > 4:
              usermsg.motd(args[1], args[2], args[3], args[4])
            else:
              es.dbgmsg(0, "usermsg motd: Syntax: motd <userid> <0 = text, 2 = url> <title> <msg>")
        elif subcommand == 'hudhint':
            if len(args) > 2:
              usermsg.hudhint(args[1], args[2])
            else:
              es.dbgmsg(0, "usermsg hudhint: Syntax: hudhint <userid> <msg>")
        elif subcommand == 'keyhint':
            if len(args) > 2:
              usermsg.keyhint(args[1], args[2])
            else:
              es.dbgmsg(0, "usermsg keyhint: Syntax: keyhint <userid> <msg>")
        elif subcommand == 'centermsg':
            if len(args) > 2:
              usermsg.centermsg(args[1], args[2])
            else:
              es.dbgmsg(0, "usermsg centermsg: Syntax: centermsg <userid> <msg>")
        elif subcommand == 'echo':
            if len(args) > 2:
              usermsg.echo(args[1], args[2])
            else:
              es.dbgmsg(0, "usermsg echo: Syntax: echo <userid> <msg>")
        else:
            es.dbgmsg(0, 'usermsg: Invalid subcommand, type "usermsg list" to see a list of valid subcommands')
    else:
        es.dbgmsg(0, 'usermsg: Missing userid and subcommand, type "usermsg list" to see a list of valid subcommands')

