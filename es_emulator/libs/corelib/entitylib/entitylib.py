# ./addons/eventscripts/corelib/entitylib/entitylib.py
# ported to Python by Hunter
# original command by Einlanzers

# Special thanks to Einlanzers who provided a lot of
#   research for this script.
# setentname
# setentname <entity-index#> <desired-name>
# This command allows you to set an entities name
#   to whatever you want. It is supposed to be a lot
#   like the EST command "est_setentname", but this version
#   is a bit buggier because it requires a player to be present
#   in order to work. Better implementations are *very* welcome,
#   but this has been very difficult to get this far.

import es
import cmdlib

import vecmath
import playerlib

gamename = es.getGameName()

def load():
    cmdlib.registerServerCommand('setentname', setentname_cmd, 'Sets an entity name. Syntax: setentname <entity-index#> <desired-name>')

def unload():
    cmdlib.unregisterServerCommand('setentname')

def setentname_cmd(args):
    if gamename in ['cstrike', 'dod', 'hl2mp']:
        userid = es.getuserid()
        if userid:
            if len(args) > 1:
                entity = args[0]
                entityname = args[1]
                if entity.isdigit() and entityname:
                    player = playerlib.getPlayer(userid)
                    playerlocation = vecmath.vector(player.getLocation())
                    playermovetype = es.getplayerprop(int(player), 'CBaseEntity.movetype')
                    if gamename == 'cstrike':
                        playerviewangles = vecmath.vector((float(es.getplayerprop(int(player), 'CCSPlayer.m_angEyeAngles[0]')), float(es.getplayerprop(int(player), 'CCSPlayer.m_angEyeAngles[1]')), 0.0))
                        playerviewoffset = vecmath.vector((float(es.getplayerprop(int(player), 'CBasePlayer.localdata.m_vecViewOffset[0]')), float(es.getplayerprop(int(player), 'CBasePlayer.localdata.m_vecViewOffset[1]')), float(es.getplayerprop(int(player), 'CBasePlayer.localdata.m_vecViewOffset[2]'))))
                    elif gamename == 'dod':
                        playerviewangles = vecmath.vector((float(es.getplayerprop(int(player), 'CDODPlayer.m_angEyeAngles[0]')), float(es.getplayerprop(int(player), 'CDODPlayer.m_angEyeAngles[1]')), 0.0))
                        playerviewoffset = vecmath.vector((float(es.getplayerprop(int(player), 'CBasePlayer.localdata.m_vecViewOffset[0]')), float(es.getplayerprop(int(player), 'CBasePlayer.localdata.m_vecViewOffset[1]')), float(es.getplayerprop(int(player), 'CBasePlayer.localdata.m_vecViewOffset[2]'))))
                    elif gamename == 'hl2mp':
                        playerviewangles = vecmath.vector((float(es.getplayerprop(int(player), 'CHL2MP_Player.m_angEyeAngles[0]')), float(es.getplayerprop(int(player), 'CHL2MP_Player.m_angEyeAngles[1]')), 0.0))
                        playerviewoffset = vecmath.vector((float(es.getplayerprop(int(player), 'CHL2MP_Player.baseclass.baseclass.baseclass.baseclass.m_vecViewOffset[0]')), float(es.getplayerprop(int(player), 'CHL2MP_Player.baseclass.baseclass.baseclass.baseclass.m_vecViewOffset[1]')), float(es.getplayerprop(int(player), 'CHL2MP_Player.baseclass.baseclass.baseclass.baseclass.m_vecViewOffset[2]'))))
                    playerviewvector = (vecmath.vector(vecmath.angles((1.0,1.0,1.0), playerviewangles))) * 0.5
                    entitylocation = vecmath.vector(es.getindexprop(entity, 'CBaseEntity.m_vecOrigin'))
                    entityviewvector = (playerlocation - (playerviewoffset + playerviewvector)) + entitylocation
                    player.freeze(1)
                    player.setLocation(list(entityviewvector))
                    player.viewCoord(list(entitylocation))
                    es.entsetname(int(player), entityname)
                    es.server.cmd('es_xsetang %s %s %s' % (int(player), playerviewangles[0], playerviewangles[1]))
                    es.setplayerprop(int(player), 'CBaseEntity.movetype', playermovetype)
                    player.setLocation(list(playerlocation))
                else:
                    es.dbgmsg(0, 'setentname: Invalid target user "%s" to setentname.' % target)
            else:
                es.dbgmsg(0, 'setentname: Not enough arguments to setentname. Syntax: setentname <entity-index#> <desired-name>')
        else:
            es.dbgmsg(0, 'setentname: No userid available. Sorry, no targetname set!')
    else:
        es.dbgmsg(0, 'setentname: Game "%s" is not supported. Sorry, no targetname set!' % gamename)
