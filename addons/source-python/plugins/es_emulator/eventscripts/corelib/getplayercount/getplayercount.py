# ./addons/eventscripts/corelib/getplayercount/getplayercount.py
# ported to Python by Hunter

import es
import cmdlib

import playerlib

def load():
    cmdlib.registerServerCommand('getplayercount', getplayercount_cmd, 'Counts players based on a foreach filter. Syntax: getplayercount <variable> <filter>')

    for line in (
        'testcase qcreate corelib getplayercounttest "Tests getplayercount"',
        'testcase addtest getplayercounttest getplayercounttest corelib/getplayercount/testcase "Getplayercount Corelib Command Test"'):
        es.server.queuecmd(line)

def unload():
    cmdlib.unregisterServerCommand('getplayercount')

def getplayercount_cmd(args):
    if len(args) > 1:
        identifier = args[1]
        if '#' in identifier:
            identifier = identifier.replace('#', ',#')[1:]
            es.ServerVar(args[0]).set(len(playerlib.getUseridList(identifier)))
        elif identifier:
            players = 0
            for player in playerlib.getPlayerList('#all'):
                if identifier.lower() in player.attributes['name'].lower() or identifier == player.attributes['steamid'] or identifier == str(player):
                    players += 1
            es.ServerVar(args[0]).set(players)
    else:
        es.dbgmsg(0, 'getplayercount: Not enough arguments to getplayercount. Syntax: getplayercount <variable> <filter>')

def testcase():
    playercount = len(playerlib.getUseridList('#all'))
    for line in (
        'profile begin getplayercount_test',
        'testlib begin getplayercount_test "getplayercount #all"',
        'es_xset _getplayercount_testvar 0',
        'getplayercount _getplayercount_testvar #all',
        'testlib fail_unless _getplayercount_testvar equalto %s' % playercount,
        'testlib end',
        'profile end getplayercount_test'):
        es.server.cmd(line)
