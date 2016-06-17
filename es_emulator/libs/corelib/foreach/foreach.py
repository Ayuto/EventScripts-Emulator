# ./addons/eventscripts/corelib/foreach/foreach.py
# ported to Python by Hunter

import es
import cmdlib

import playerlib
import weaponlib

def load():
    cmdlib.registerServerCommand('foreach', foreach_cmd, 'Loops a command through a list of objects')

    for line in (
        'testcase qcreate corelib foreachtest "Tests foreach"',
        'testcase addtest foreachtest foreachtest corelib/foreach/testcase "Foreach Corelib Command Test"'):
        es.server.queuecmd(line)

def unload():
    cmdlib.unregisterServerCommand('foreach')

def foreach_cmd(args):
    if len(args):
        subcmd = args[0].lower()
        if subcmd == 'player':
            if len(args) > 3:
                foreach_player(es.ServerVar(args[1], ''), args[2], args[3])
            else:
                es.dbgmsg(0, 'foreach player: Invalid arguments for foreach player. Syntax: foreach player <var> <identifier> "<command>"')
        elif subcmd == 'weapon':
            if len(args) > 3:
                foreach_weapon(es.ServerVar(args[1], ''), args[2], args[3])
            else:
                es.dbgmsg(0, 'foreach weapon: Invalid arguments for foreach weapon. Syntax: foreach weapon <var> <identifier> "<command>"')
        elif subcmd == 'entity':
            if len(args) > 4:
                foreach_entity(es.ServerVar(args[1], ''), es.ServerVar(args[2], ''), args[3], args[4])
            else:
                es.dbgmsg(0, 'foreach entity: Invalid arguments for foreach entity. Syntax: foreach entity <keyvar> <classvar> <classname> "<command>"')
        elif subcmd == 'token':
            if len(args) > 4:
                foreach_token(es.ServerVar(args[1], ''), args[2], args[3], args[4])
            else:
                es.dbgmsg(0, 'foreach: Invalid arguments for foreach token. Syntax: foreach token <var> "<string>" "<separator>" "<command>"')
        elif subcmd == 'part':
            if len(args) > 4:
                foreach_part(es.ServerVar(args[1], ''), args[2], args[3], args[4])
            else:
                es.dbgmsg(0, 'foreach: Invalid arguments for foreach part. Syntax: foreach part <var> "<string>" "<character count>" "<command>"')
        else:
            es.dbgmsg(0, 'foreach: Invalid subcommand for foreach')
    else:
        es.dbgmsg(0, 'foreach: Missing subcommand for foreach')


def foreach_player(variable, identifier, command):
    if '#' in identifier:
        identifier = identifier.replace('#', ',#')[1:]
        for userid in playerlib.getUseridList(identifier):
            variable.set(int(userid))
            es.server.cmd(command)
    elif identifier:
        for player in playerlib.getPlayerList('#all'):
            if identifier.lower() in player.attributes['name'].lower() or identifier == player.attributes['steamid'] or identifier == str(player):
                variable.set(int(player))
                es.server.cmd(command)
    else:
        es.dbgmsg(0, 'foreach player: The identifier "%s" does not exists' % identifier)

def foreach_weapon(variable, identifier, command):
    if '#' in identifier:
        identifier = identifier.replace('#hand', '#melee').replace('#nade', '#grenade')
        identifier = identifier.replace('#', ',#')[1:]
        weapons = []
        for weapon in identifier.split(","):
            weapons.extend(weaponlib.getWeaponNameList(weapon))
        while weapons:
            weapon = weapons[0]
            variable.set(str(weapon))
            es.server.cmd(command)
            while weapon in weapons: weapons.remove(weapon)
    else:
        es.dbgmsg(0, 'foreach weapon: The identifier "%s" does not exists' % identifier)

def foreach_entity(variable, classvariable, identifier, command):
    if identifier:
        entities = es.createentitylist(identifier)
        for entity in entities:
            variable.set(str(entity))
            classvariable.set(str(entities[entity]['classname']))
            es.server.cmd(command)
    else:
        es.dbgmsg(0, 'foreach entity: The identifier "%s" does not exists' % identifier)

def foreach_token(variable, string, seperator, command):
    for token in string.split(seperator):
        if len(token):
            variable.set(str(token))
            es.server.cmd(command)

def foreach_part(variable, string, charcount, command):
    for offset in range(0, len(string)+int(charcount), int(charcount)):
        if len(str(string)[offset:offset+int(charcount)]):
            variable.set(str(string)[offset:offset+int(charcount)])
            es.server.cmd(command)

def testcase():
    playercount = len(playerlib.getUseridList('#all'))
    weaponcount = len(weaponlib.getWeaponList('#all'))
    entitycount = len(es.createentitylist('env_fire'))
    for line in (
        'profile begin foreach_test',
        'profile begin foreach_player',
        'testlib begin foreach_player "foreach player #all"',
        'es_xset _foreach_count 0',
        'foreach player _foreach_testvar #all "es_xmath _foreach_count + 1"',
        'testlib fail_unless _foreach_count equalto %d' % playercount,
        'testlib end',
        'profile end foreach_player',
        'profile begin foreach_weapon', 
        'testlib begin foreach_weapon "foreach weapon #all"',
        'es_xset _foreach_count 0',
        'foreach weapon _foreach_testvar #all "es_xmath _foreach_count + 1"',
        'testlib fail_unless _foreach_count equalto %d' % weaponcount,
        'testlib end',
        'profile end foreach_weapon',
        'profile begin foreach_entity',
        'testlib begin foreach_entity "foreach entity env_fire"',
        'es_xset _foreach_count 0',
        'foreach entity _foreach_testvar _foreach_testvar env_fire "es_xmath _foreach_count + 1"',
        'testlib fail_unless _foreach_count equalto %d' % entitycount,
        'testlib end',
        'profile end foreach_entity',
        'profile begin foreach_token',
        'testlib begin foreach_token "foreach token"',
        'es_xset _foreach_count 0',
        'foreach token _foreach_testvar "a-ab-abc-abcd-abcde" - "es_xmath _foreach_count + 1"',
        'testlib fail_unless _foreach_count equalto 5',
        'testlib end',
        'profile end foreach_token',
        'profile begin foreach_part',
        'testlib begin foreach_part "foreach part"',
        'es_xset _foreach_count 0',
        'foreach part _foreach_testvar "a1b2c3d4e5" 2 "es_xmath _foreach_count + 1"',
        'testlib fail_unless _foreach_count equalto 5',
        'testlib end',
        'profile end foreach_part',
        'profile end foreach_test'):
        es.server.cmd(line)
