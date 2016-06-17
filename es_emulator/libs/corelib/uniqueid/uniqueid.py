# ./addons/eventscripts/corelib/uniqueid/uniqueid.py
import es
import cmdlib

import playerlib

def load():
    cmdlib.registerServerCommand('uniqueid', uniqueid_cmd, 'uniqueid <var> <userid> [add botname]')

def unload():
    cmdlib.unregisterServerCommand('uniqueid')

def uniqueid_cmd(args):
    ''' Console command to return the uniqueid for a player or a bot.
        If you want the bot's actual name, provide the final optional parameter.
        uniqueid <var> <userid> [add botname]'''
    if len(args) in (2, 3):
        returnvar = es.ServerVar(args[0])
        # get the uniqueid, telling it to append botname if the final arg is given
        id = playerlib.uniqueid(userid=args[1], botname=(args[2] if len(args) == 3 else None))
        returnvar.set(id)
    else:
        es.dbgmsg(0, 'Syntax: uniqueid <var> <userid> [add botname]')
