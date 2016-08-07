# Date of release 05/12/2008
import es
import langlib
import math
import weaponlib

import collections
import operator


# Plugin information
info = es.AddonInfo()
info['name'] = "Playerlib EventScripts python library"
info['version'] = "250-r860"
info['authors'] = "Don and the ES development team"
info['url'] = "http://python.eventscripts.com/pages/Playerlib"
info['description'] = "Provides and sets player information"


""" Global variables """

# this will be our global list of filters
filters = {}

# Weapon and ammo information
_primary_weapons   = weaponlib.getWeaponList('#primary')
_secondary_weapons = weaponlib.getWeaponList('#secondary')
_weapons_ammo = dict([(weapon, weapon.prop) for weapon in weaponlib.getWeaponList('#all')])

_lastgive = es.ServerVar('eventscripts_lastgive') # We use this more than once so we might as well have only one instance
_gamename = es.getGameName() # We need the game name for a few purposes

# Player class attributes that have sub-attributes
_attribute_recursion = ('ammo', 'clip', 'weaponindex', 'distance', 'obstructionbetween', 'nearplayer', 'closestplayerbyteam')
# Player class attributes that can be called as well as get or set
_callable_attributes = ('push', 'noclip', 'noblock', 'jetpack', 'freeze', 'flash', 'godmode', 'burn', 'extinguish', 'uniqueid')

# Eye angle property
def _getEyeAngle():
   if _gamename in ('cstrike', 'left4dead', 'left4dead2'):
      return 'CCSPlayer.m_angEyeAngles[%s]'
   elif _gamename == 'dod':
      return 'CDODPlayer.m_angEyeAngles[%s]'
   elif _gamename == 'tf':
      return 'CTFPlayer.tfnonlocaldata.m_angEyeAngles[%s]'
   elif _gamename in ('hl2mp', 'ageofchivalry', 'diprip', 'fistful_of_frags', 'gesource',
    'hl2ctf', 'smashball', 'so', 'sourceforts', 'synergy', 'zombie_master', 'zps'):
      return 'CHL2MP_Player.m_angEyeAngles[%s]'
   elif _gamename in ('hl2', 'episodic', 'ep2'):
      return 'CBaseFlex.m_vecViewOffset[%s]'
   elif _gamename == 'portal':
      return 'CPortal_Player.m_angEyeAngles[%s]'
   elif _gamename in ('ag2', 'Jailbreak'):
      return 'CHL2MP_Player.hl2mpnonlocaldata.m_angEyeAngles[%s]'
   elif _gamename == 'dystopia':
      return 'CDYSPlayer.m_angEyeAngles[%s]'
   elif _gamename == 'esmod':
      return 'CESPlayer.m_angEyeAngles[%s]'
   elif _gamename == 'FortressForever':
      return 'CFFPlayer.m_angEyeAngles[%s]'
   elif _gamename in ('empires', 'hidden'):
      return 'CSDKPlayer.m_angEyeAngles[%s]'
   elif _gamename == 'hl1mp':
      return 'CHL1MP_Player.m_angEyeAngles[%s]'
   elif _gamename == 'insurgency':
      return 'CINSPlayer.sensdata.m_angEyeAngles[%s]'
   elif _gamename == 'NeotokyoSource':
      return 'CNEOPlayer.m_angEyeAngles[%s]'
   elif _gamename == 'pvkii':
      return 'CPVK2Player.m_angEyeAngles[%s]'
   elif _gamename == 'sgtls':
      return 'CTLSPlayer.nonlocaldata.m_angEyeAngles[%s]'
   return ''
_eyeangle = _getEyeAngle()

""" Custom exceptions """

# custom exceptions we can throw.
# This probably needs more added to it, but it should be fine.
class _PlayerlibError(Exception): pass

class UseridError(_PlayerlibError): pass

class PlayerError(_PlayerlibError): pass

""" Player class """

# Scripters won't instatiate this class directly. They'll probably use:
# myPlayer = playerlib.getPlayer(userid)
# myPlayerList = playerlib.getPlayerList(filtername)

# THOUGHTS: Right now it seems a Player object will be somewhat of a static
#  view of a player for some information, but might be on-the-fly for playergetset
#  info. How do we make that clear to scripters? Or do we take the performance
#  hit and make everything dynamic even though right now that requires
#  refreshing all of the es.createplayerlist() attributes at once?
class Player(object):
    class ReturnValue:
        """
        Allows integer or float return values to be coerced into other data types.
        This class preserves backwards-compatibility while also allowing more intuitive comparisons.
        """
        call_func = None
        def __init__(self, value):
            self.value = str(value)
        def __getattr__(self, value):
            if hasattr(str, value) and not hasattr(Player.ReturnValue, value):
                return getattr(str(self), value)
        def __call__(self, *a, **kw):
            if not isinstance(self.call_func, collections.Callable):
                raise TypeError("'ReturnValue' object is not callable")
            return self.call_func(*a, **kw)
        def __str__(self):
            return self.value
        def __int__(self):
            return int(self.value)
        def __float__(self):
            return float(self.value)
        def __bool__(self):
            return bool(int(self))
        def __lt__(self, other):
            return es._compare_value(self, other, operator.lt)
        def __le__(self, other):
            return es._compare_value(self, other, operator.le)
        def __eq__(self, other):
            return es._compare_value(self, other, operator.eq)
        def __ne__(self, other):
            return es._compare_value(self, other, operator.ne)
        def __ge__(self, other):
            return es._compare_value(self, other, operator.ge)
        def __gt__(self, other):
            return es._compare_value(self, other, operator.gt)

    class AttributeLevel(object):
        """ Provides a sub-attribute level for any get/set attributes requiring it. """
        _parent = None
        _name   = ''
        def __init__(self, parent, name):
            self._parent = parent
            self._name   = name
        def __getattr__(self, name):
            if hasattr(Player.AttributeLevel, name):
                return getattr(self, name)
            try:
                return self.__getitem__(name)
            except KeyError as e:
                raise AttributeError(e)
        def __setattr__(self, name, value):
            if name.startswith('_') or hasattr(Player.AttributeLevel, name):
                object.__setattr__(self, name, value)
            else:
                try:
                    self.__setitem__(name, value)
                except KeyError as e:
                    raise AttributeError(e)
        def __getitem__(self, name):
            return self._parent.get(self._name, name)
        def __setitem__(self, name, value):
            return self._parent.set(self._name, (name, value))

    class LockedDictionary(dict):
        """ Creates a dictionary that can be initialized but not changed -- created for player attributes """
        def __detattr__(self, name):
            self._error()
        def __delitem__(self, name):
            self._error()
        def __setattr__(self, name, value):
            self._error()
        def __setattribute__(self, name, value):
            self._error()
        def __setitem__(self, name, value):
            self._error()
        def clear(self):
            self._error()
        def pop(self, *a, **kw):
            self._error()
        def popitem(self):
            self._error()
        def setdefault(*a):
            self._error()
        def update(self, *a, **kw):
            self._error()
        def _error(self):
            raise KeyError('LockedDictionary instances cannot be changed')

    """ Begin Player class functions """

    # These must be here for __setattr__ to recognize them as valid attributes to set
    userid = 0
    attributes = {}
    def __init__(self, playerid):
        """ Initialization of Player class with a userid. """
        # We'll be nice and convert the playerid to an int in case they gave
        # us a string userid.
        if not str(playerid).isdigit():
            raise TypeError("'" + str(playerid) + "' is an invalid userid")
        self.userid = int(playerid)
        # Check if it's a valid userid. Otherwise we throw.
        if not self.isOnline():
            raise UseridError("'" + str(playerid) + "' is an invalid userid")
        # Maybe use es.createplayerlist(userid) to get initial values?
        self.refreshAttributes()
        # TODO: What else do we need to initialize?

    def refreshAttributes(self):
        """
        Refresh the attributes for this player from ES. These are cached in
        the player object for performance.
        """
        # If this fails maybe they gave us the wrong userid, so maybe it should
        # except all the way up? Probably need a cleaner exception, though.
        try:
            self.attributes = es.createplayerlist(self.userid)[self.userid]
            if 'weapon' in self.attributes:
                newweapon = weaponlib.getWeapon(self.attributes['weapon'])
                if newweapon:
                    self.attributes['weapon'] = newweapon
            self.attributes = self.LockedDictionary(self.attributes)
        except KeyError:
            raise PlayerError('Player has left server')

    """ Object overrides """

    def __getattr__(self, name):
        """
        Returns normal class attributes and passes unknown attributes to
        __getitem__ for a possible use with the "get" function.
        """
        if hasattr(Player, name):
            return getattr(self, name)
        else:
            try:
                return self.__getitem__(name)
            except KeyError as e:
                raise AttributeError(e)

    def __getitem__(self, name):
        """
        Passes the item name to the "get" function and returns the result.
        If the item requires sub-attributes we return an AttributeLevel class instead.
        """
        if name in _attribute_recursion:
            return self.AttributeLevel(self, name) # The current item requires a sub-attribute
        else:
            e = None
            try:
                return_val = self.get(name)
            except KeyError as e:
                return_val = None
            if name in _callable_attributes: # If the item is also callable we need ReturnValue to make it callable
                return_val = self.ReturnValue(return_val)
                return_val.call_func = getattr(self, '_' + name)
            if return_val is None and not e is None:
                raise KeyError(e)
            return return_val

    def __setattr__(self, name, value):
        """
        Sets normal class attributes and passes unknown attributes to
        __setitem__ for possible use with the "set" function.
        """
        if name.startswith('_') or hasattr(Player, name):
            object.__setattr__(self, name, value)
        else:
            try:
                self.__setitem__(name, value)
            except KeyError as e:
               raise AttributeError(e)

    def __setitem__(self, name, value):
        """ Passes the item name and desired value to the "set" function """
        self.set(name, value)

    def __int__(self):
        """ Returns the integer userid of the player when the instance is cast to an integer. """
        return self.userid

    def __str__(self):
        """ Returns the string of the player's userid mostly for string formatting (%s) """
        return str(self.userid)

    """ Get functions """

    def getPrimary(self):
        """ Returns the name of the player's primary weapon returning False if no weapon is found. """
        for weapon in _primary_weapons:
            if self.getWeaponIndex(weapon):
                return weapon
        return self.ReturnValue('0')

    def getSecondary(self):
        """ Returns the name of the player's secondary weapon returning False if no weapon is found. """
        for weapon in _secondary_weapons:
            if self.getWeaponIndex(weapon):
                return weapon
        return self.ReturnValue('0')

    def getHE(self):
        """ Returns the number of HE grenades the player has. """
        return es.getplayerprop(self.userid, "CBasePlayer.localdata.m_iAmmo.011")

    def getFB(self):
        """ Returns the number of flashbangs the player has. """
        return es.getplayerprop(self.userid, "CBasePlayer.localdata.m_iAmmo.012")

    def getSG(self):
        """ Returns the number of smoke grenades the player has. """
        return es.getplayerprop(self.userid, "CBasePlayer.localdata.m_iAmmo.013")

    def hasC4(self):
        """ Returns True if the player has C4 otherwise returns False. """
        return self.ReturnValue('1' if self.getWeaponIndex('weapon_c4') else '0')

    def getAmmo(self, weapon):
        """
        Returns the player's ammo for the specified weapon or weapon type, returning
        False if the player has no corresponding weapon.
        "weapon" parameter is either a weapon name, 'primary' (or '1') or 'secondary' (or '2').
        """
        if weapon in ('1', 'primary'):
            weapon_name = self.getPrimary()
        elif weapon in ('2', 'secondary'):
            weapon_name = self.getSecondary()
        else:
            weapon_name = weaponlib.getWeapon(weapon)
        if not weapon_name:
            return self.ReturnValue(0)
        return es.getplayerprop(self.userid, _weapons_ammo[weapon_name])

    def getClip(self, weapon):
        """
        Returns the player's clip amount for the specified weapon or weapon type, returning
        False if the player has no corresponding weapon.
        "weapon" parameter is either a weapon name, 'primary' (or '1') or 'secondary' (or '2').
        """
        if weapon in ('1', 'primary'):
            weapon_name = self.getPrimary()
        elif weapon in ('2', 'secondary'):
            weapon_name = self.getSecondary()
        else:
            weapon_name = weaponlib.getWeapon(weapon)
        if not weapon_name:
            return self.ReturnValue('0')
        index = self.getWeaponIndex(weapon_name)
        if not index:
            raise ValueError("Player has no '%s' weapon" % weapon)
        if _gamename == 'left4dead2':
            return es.getindexprop(index, 'CBaseCombatWeapon.m_iClip1')
        else:
            return es.getindexprop(index, 'CBaseCombatWeapon.LocalWeaponData.m_iClip1')

    def getWeaponIndex(self, weapon):
        """
        Returns the index of the specified weapon held by the player.
        Returns 0 if the player doesn't have the specified weapon.
        """
        weapon_to_find = weaponlib.getWeapon(weapon)
        if weapon_to_find is None:
            raise ValueError("'%s' is not a valid weapon" % weapon)
        handle = es.getplayerhandle(self.userid)
        for index in weapon_to_find.indexlist:
            if es.getindexprop(index, "CBaseCombatWeapon.m_hOwner") == handle:
                return index
        return 0

    def getWeaponList(self):
        """ Returns a list of the player's weapons (only weapons with unique indexes). """
        handle = es.getplayerhandle(self.userid)
        weaponlist = []
        for index, weapon in weaponlib.getWeaponIndexList():
            if es.getindexprop(index, 'CBaseEntity.m_hOwnerEntity') == handle:
                weaponlist.append(weapon)
        return weaponlist

    def getViewAngle(self):
        """ Returns the player's view angle. """
        if _eyeangle.count('%s') != 1:
            raise NotImplementedError('getViewAngle does not support game "' + _gamename + '"')
        myRotation  = es.getplayerprop(self.userid, "CBaseEntity.m_angRotation").split(',')[2]
        myEyeAngle0 = es.getplayerprop(self.userid, _eyeangle % 0)
        myEyeAngle1 = es.getplayerprop(self.userid, _eyeangle % 1)
        return (myEyeAngle0, (myEyeAngle1 + 360) if myEyeAngle1 < 0 else myEyeAngle1, float(myRotation))

    def getCash(self):
        """ Returns the player's cash amount. """
        return es.getplayerprop(self.userid, "CCSPlayer.m_iAccount")

    def getHealth(self):
        """ Returns the player's health amount. """
        return es.getplayerprop(self.userid, "CBasePlayer.m_iHealth")

    def getArmor(self):
        """ Returns the player's armor amount. """
        return es.getplayerprop(self.userid, "CCSPlayer.m_ArmorValue")

    def getSpeed(self):
        """ Returns the player's speed multiplier. """
        return es.getplayerprop(self.userid, "CBasePlayer.localdata.m_flLaggedMovementValue")

    def hasDefuser(self):
        """ Returns 1 if the player has a defuse kit otherwise returns 0. """
        return es.getplayerprop(self.userid, "CCSPlayer.m_bHasDefuser") % 2

    def viewVector(self):
        """ Returns the player's view vector. """
        if _eyeangle.count('%s') != 1:
            raise NotImplementedError('viewVector does not support game "' + _gamename + '"')
        myEyeAngle0 = es.getplayerprop(self.userid, _eyeangle % 0)
        myEyeAngle1 = es.getplayerprop(self.userid, _eyeangle % 1)
        myX = math.cos(math.radians(myEyeAngle1))
        myY = math.sin(math.radians(myEyeAngle1))
        myZ = -1 * math.sin(math.radians(myEyeAngle0))
        return (myX, myY, myZ)

    def getDistance(self, value, plane='xyz'):
        """
        Returns the player's distance to a player or coordinate on the given plane.
        "value" parameter can either be a three-element iterable of coordinates or a userid.
        """
        if hasattr(value, '__iter__'):
            if isinstance(value, dict):
                raise TypeError("getDistance coordinates cannot be type 'dict'")
            his_x, his_y, his_z = list(map(float, value))
        else:
            target_userid = getPlayer(value).userid # If the target is invalid we'd rather throw a descriptive error
            his_x, his_y, his_z = es.getplayerlocation(target_userid)
        my_x, my_y, my_z = es.getplayerlocation(self.userid)
        myX = my_x - his_x
        myY = my_y - his_y
        myZ = my_z - his_z
        if plane == 'x':
            return myX
        elif plane == 'y':
            return myY
        elif plane == 'z':
            return myZ
        elif plane == 'xy':
            return (myX ** 2 + myY ** 2) ** 0.5
        elif plane == 'xz':
            return (myX ** 2 + myZ ** 2) ** 0.5
        elif plane == 'yz':
            return (myY ** 2 + myZ ** 2) ** 0.5
        elif plane == 'xyz':
            return (myX ** 2 + myY ** 2 + myZ ** 2) ** 0.5
        return self.ReturnValue('0')

    def getNoClip(self):
        """ Returns True if the player is in noclip mode otherwise returns False. """
        return self.ReturnValue('1' if es.getplayerprop(self.userid, "CBaseEntity.movetype") == 8 else '0')

    def getNoBlock(self):
        """ Returns True if the player is in noblock mode otherwise returns False. """
        return self.ReturnValue('1' if es.getplayerprop(self.userid, "CBaseEntity.m_CollisionGroup") == 2 else '0')

    def getJetpack(self):
        """ Returns True if the player is in jetpack mode otherwise returns False. """
        return self.ReturnValue('1' if es.getplayerprop(self.userid, "CBaseEntity.movetype") == 4 else '0')

    def getFreeze(self):
        """ Returns True if the player is frozen otherwise returns False. """
        return self.ReturnValue('1' if es.getplayerprop(self.userid, "CBaseEntity.movetype") == 0 else '0')

    def getLocation(self):
        """ Returns the player's location in a three-element tuple. """
        return es.getplayerlocation(self.userid)

    def getFlashAlpha(self):
        """ Returns the player's flash alpha value (0 to 255). """
        return es.getplayerprop(self.userid, "CCSPlayer.m_flFlashMaxAlpha")

    def getFlashDuration(self):
        """ Returns the player's flash duration in seconds. """
        return es.getplayerprop(self.userid, "CCSPlayer.m_flFlashDuration")

    def getFlash(self):
        """ Returns a two-element tuple of the player's flash alpha and duration, respectively. """
        return self.getFlashAlpha(), self.getFlashDuration()

    def getColor(self):
        """ Returns a four-element tuple of the player's color in RGBA format. """
        color = es.getplayerprop(self.userid, "CBaseEntity.m_clrRender")
        return tuple(int(x) for x in (color & 0xff, (color & 0xff00) >> 8, (color & 0xff0000) >> 16, (color & 0xff000000) >> 24))

    def getLanguage(self):
        """ Returns the player's language setting for use with langlib. """
        lang = self.attributes.get('language', 0)
        if lang:
            return langlib.getLangAbbreviation(lang)
        return langlib.getDefaultLang()

    def isDucked(self):
        """ Returns 1 if the player is ducked otherwise returns 0. """
        return es.getplayerprop(self.userid, 'CBasePlayer.localdata.m_Local.m_bDucked') % 2

    def hasNightvision(self):
        """ Returns 1 if the player has night vision otherwise returns 0. """
        return es.getplayerprop(self.userid, 'CCSPlayer.m_bHasNightVision') % 2

    def getNightvisionState(self):
        """ Returns 1 if the player's nightvision is on otherwise returns 0. """
        return es.getplayerprop(self.userid, 'CCSPlayer.m_bNightVisionOn') % 2

    def getNightvisionOn(self, *a, **kw):
        """ Wraps getNightvisionState """
        return self.getNightvisionState(*a, **kw)

    def inBuyZone(self):
        """ Returns 1 if the player is in a buy zone otherwise returns 0. """
        return es.getplayerprop(self.userid, 'CCSPlayer.m_bInBuyZone') % 2

    def inBombZone(self):
        """ Returns 1 if the player is in a bomb zone otherwise returns 0. """
        return es.getplayerprop(self.userid, 'CCSPlayer.m_bInBombZone') % 2

    def inRescueZone(self):
        """ Returns 1 if the player is in a rescue zone otherwise returns 0. """
        return es.getplayerprop(self.userid, 'CCSPlayer.m_bInHostageRescueZone') % 2

    def isDefusing(self):
        """ Returns 1 if the player is defusing the bomb otherwise returns 0. """
        return es.getplayerprop(self.userid, 'CCSPlayer.m_bIsDefusing') % 2

    def hasHelmet(self):
        """ Returns 1 if the player has a helmet otherwise returns 0. """
        return es.getplayerprop(self.userid, 'CCSPlayer.m_bHasHelmet') % 2

    def onGround(self):
        """ Returns 1 if the player is on the ground otherwise returns 0. """
        return es.getplayerprop(self.userid, 'CBasePlayer.m_fFlags') & 1

    def inGodMode(self):
        """ Returns True if the player is in god mode otherwise returns False. """
        return not es.getplayerprop(self.userid, "CBasePlayer.m_lifeState")

    def getWeaponColor(self):
        """ Returns the color of the player's active weapon. """
        index = self.getWeaponIndex(self.getAttribute('weapon'))
        if index:
            color = es.getindexprop(index, "CBaseEntity.m_clrRender")
            return tuple(int(x) for x in (color & 0xff, (color & 0xff00) >> 8, (color & 0xff0000) >> 16, (color & 0xff000000) >> 24))
        else:
            raise KeyError("Player has no active weapon")

    def getViewCoord(self):
        """ Returns the coordinates where the player's aiming reticle is pointing. """
        es.server.cmd('es_xprop_dynamic_create %s props_c17/tv_monitor01_screen.mdl' % self.userid)
        location = es.getindexprop(_lastgive, 'CBaseEntity.m_vecOrigin')
        es.server.cmd('es_xremove ' + _lastgive)
        return location

    def getEyeLocation(self):
        """ Returns the coordinates of the player's eyes. """
        return tuple(es.getplayerprop(self.userid, 'CBasePlayer.localdata.m_vecViewOffset[' + str(x) + ']') + y for x, y in enumerate(es.getplayerlocation(self.userid)))

    def isObstructionBetween(self, value):
        """
        Returns True if there is a wall between the line of sight between the player
        and another player or set of coordinates, otherwise returns False.
        """
        if hasattr(value, '__iter__'): # Is the value a set of coordinates?
            if len(value) != 3:
                raise ValueError('isObstructionBetween coordinates must have exactly three elements')
            end_location = list(value)
        elif es.getuserid(value): # Is the value a userid?
            end_location = getPlayer(es.getuserid(value)).getEyeLocation() # If given a userid, we want the player's eye location
        else: # Argument not recognized
            raise ValueError('isObstructionBetween requires a three-element iterable of coordinates or a userid')

        start_eyeangle = self.getViewAngle()
        start_location = self.getEyeLocation()
        if self.getDistance(end_location) <= 40:
            return False # If the coordinates are close enough there is no wall between them

        # Force the player to look at the coordinates and then check if the player's view coord is
        # between the start and end locations
        self.lookAt(end_location)
        view_location = list(map(float, self.getViewCoord().split(',')))
        result = True
        for x in (0, 1, 2):
            if not min(start_location[x], end_location[x]) <= view_location[x] <= max(start_location[x], end_location[x]):
                result = False
                break

        # Revert the player's eye angles and return the final result
        es.server.cmd('es_xsetang %s %s %s %s' % ((self.userid,) + start_eyeangle))
        return result

    def getNearPlayers(self, distance):
        """ Returns a list of userids of players within the distance specified by the "distance" parameter. """
        nearlist   = []
        distance   = int(distance)
        x1, y1, z1 = es.getplayerlocation(self.userid)
        for id in es.getUseridList():
            if id != self.userid and not es.getplayerprop(id, 'CBasePlayer.pl.deadflag'):
                x2, y2, z2 = es.getplayerlocation(id)
                if ((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) ** 0.5 <= distance:
                    nearlist.append(id)
        return nearlist

    def getClosestPlayer(self, team=None):
        """ Returns the userid of the closest player, on a certain team if specified. """
        x1, y1, z1 = es.getplayerlocation(self.userid)
        if not team:
            team = (2, 3)
        else:
            team = (int(team),)
        player_distance = []
        for id in es.getUseridList():
            if self.userid != id and es.getplayerteam(id) in team and not es.getplayerprop(id, 'CBasePlayer.pl.deadflag'):
                x2, y2, z2 = es.getplayerlocation(id)
                player_distance.append((((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) ** 0.5, id))
        return min(player_distance) if player_distance else (None, None)

    def _uniqueid(self, botname=False):
        """ Returns a unique id for the player. Call without underscore, i.e.: player.uniqueid([botname]) """
        # We start with the player's Steam ID
        uniqueid = es.getplayersteamid(self.userid)
        if 'LAN' in uniqueid:
            # LAN players
            address  = es.createplayerlist(self.userid)[self.userid]['address'].split(':')[0]
            uniqueid = 'LAN_%d:%s' % (len(address), address.replace('.',''))
        elif uniqueid == 'BOT' and botname:
            # BOTs with names attached
            uniqueid = ('BOT_%s' % es.getplayername(self.userid)).upper()
        return uniqueid

    def getAttribute(self, attribute):
        """ Returns attributes obtained with es.createplayerlist. """
        return self.attributes[attribute]


    def get(self, param, passparam=""):
        """
        Including all parameters from the original playerget, this function takes string parameters
        for all player information the Player class can provide.
        This is the original method playerlib used to provide information.
        """
        param = str(param).lower()
        # passparam = str(passparam).lower()
        # GET PRIMARY
        if param == "primary":
            return self.getPrimary()
        # GET SECONDARY
        elif param == "secondary":
            return self.getSecondary()
        # GET HE GRENADE
        elif param == "he":
            return self.getHE()
        # GET FLASHBANG
        elif param == "fb":
            return self.getFB()
        # GET SMOKE GRENADE
        elif param == "sg":
            return self.getSG()
        # GET C4 - THE BOMB
        elif param == "c4":
            return self.hasC4()
        # GET WEAPON AMMO
        elif param == "ammo":
            return self.getAmmo(passparam)
        # GET WEAPON CLIP
        elif param == "clip":
            return self.getClip(passparam)
        # GET WEAPON INDEX
        elif param == "weaponindex":
            return self.getWeaponIndex(passparam)
        # GET WEAPONLIST
        elif param == "weaponlist":
            return self.getWeaponList()
        # GET VIEWANGLE
        elif param == "viewangle":
            return self.getViewAngle()
        # GET PLAYER CASH
        elif param == "cash":
            return self.getCash()
        # GET PLAYER HEALTH
        elif param == "health":
            return self.getHealth()
        # GET PLAYER ARMOR
        elif param == "armor":
            return self.getArmor()
        # GET PLAYER SPEEED
        elif param == "speed":
            return self.getSpeed()
        # GET DEFUSER
        elif param == "defuser":
            return self.hasDefuser()
        # GET VIEWVECTOR
        elif param == "viewvector":
            return self.viewVector()
        # GET DISTANCE
        elif param == "distance":
            if hasattr(passparam, '__iter__'):
                if isinstance(passparam, dict):
                    raise ValueError("getDistance userid/coordinates cannot be type 'dict'")
            else:
                passparam = (passparam,)
            return self.getDistance(*passparam)
        # GET NOCLIP
        elif param == "noclip":
            return self.getNoClip()
        # GET NOBLOCK
        elif param == "noblock":
            return self.getNoBlock()
        # GET JETPACK
        elif param == "jetpack":
            return self.getJetpack()
        # GET FREEZE
        elif param == "freeze":
            return self.getFreeze()
        # GET LOCATION
        elif param == "location":
            return self.getLocation()
        # GET FLASH ALPHA
        elif param == "flashalpha":
            return self.getFlashAlpha()
        # GET FLASH DURATION
        elif param == "flashduration":
            return self.getFlashDuration()
        # GET FLASH ALPHA AND DURATION
        elif param == "flash":
            return self.getFlash()
        # GET COLOR
        elif param == "color":
            return self.getColor()
        # GET LANG
        elif param == "lang":
            return self.getLanguage()
        # GET ISDUCKED
        elif param == "isducked":
            return self.isDucked()
        # GET NIGHTVISION
        elif param == "nightvision":
            return self.hasNightvision()
        # GET NIGHTVISIONON
        elif param in ("nightvisionon", "nightvisionstate"):
            return self.getNightvisionState()
        # GET INBUYZONE
        elif param == "inbuyzone":
            return self.inBuyZone()
        # GET INBOMBZONE
        elif param == "inbombzone":
            return self.inBombZone()
        # GET INRESCUEZONE
        elif param == "inrescuezone":
            return self.inRescueZone()
        # GET IS DEFUSING
        elif param == "isdefusing":
            return self.isDefusing()
        # GET HASHELMET
        elif param in ("hashelmet", "helmet"):
            return self.hasHelmet()
        # GET ONGROUND
        elif param == "onground":
            return self.onGround()
        # GET GODMODE
        elif param == "godmode":
            return self.inGodMode()
        # GET WEAPON COLOR
        elif param == 'weaponcolor':
            return self.getWeaponColor()
        # GET VIEWCOORD
        elif param == "viewcoord":
            return self.getViewCoord()
        # GET EYE ANGLE
        elif param == "eyeangle":
            return self.getEyeAngle()
        # GET EYE LOCATION
        elif param == "eyelocation":
            return self.getEyeLocation()
        # GET WALL BETWEEN
        elif param == "obstructionbetween":
            return self.isObstructionBetween(passparam)
        # GET NEARPLAYER
        elif param in ("nearplayer", "nearplayers"):
            return self.getNearPlayers(passparam)
        # GET CLOSEST PLAYER
        elif param in ("closestplayer", "closestplayerbyteam"):
            return self.getClosestPlayer(passparam)
        # GET UNIQUEID
        elif param == "uniqueid":
            return self._uniqueid(passparam)
        # GET USERID
        elif param == "userid":
            return self.userid
        # GET TEAM
        elif param == "team":
            return self.getAttribute("teamid")
        # GET ATTRIBUTES
        elif param in self.attributes:
            return self.getAttribute(param)
        raise KeyError("Cannot get '%s' info for player" % param)

    """ Set functions """

    def setAmmo(self, weapon, value):
        """ Sets the ammo for the specified weapon or raises ValueError if the weapon is invalid. """
        weapon = weaponlib.getWeapon(weapon)
        if weapon is None:
            raise ValueError("'%s' is an invalid weapon" % weapon)
        es.setplayerprop(self.userid, weapon.prop, int(value)) # Cast to integer to raise a Value error if invalid value

    def setPrimaryAmmo(self, value):
       """ Sets the ammo for the player's primary weapon or raises KeyError if the player has no primary weapon. """
       weapon = self.getPrimary()
       if weapon is None:
           raise KeyError('Player has no primary weapon')
       self.setAmmo(weapon, value)

    def setSecondaryAmmo(self, value):
       """ Sets the ammo for the player's secondary weapon or raises KeyError if the player has no secondary weapon. """
       weapon = self.getSecondary()
       if weapon is None:
           raise KeyError('Player has no secondary weapon')
       self.setAmmo(weapon, value)

    def setClip(self, weapon, value):
        """ Sets the clip amount for the specified weapon or raises ValueError if the weapon is invalid. """
        weapon = weaponlib.getWeapon(weapon)
        if weapon is None:
            raise ValueError("'%s' is an invalid weapon" % weapon)
        index = self.getWeaponIndex(weapon)
        if index:
            if _gamename == 'left4dead2':
                es.setindexprop(index, "CBaseCombatWeapon.m_iClip1", value)
            else:
                es.setindexprop(index, "CBaseCombatWeapon.LocalWeaponData.m_iClip1", value)
        else:
            raise KeyError("Player has no '%s' weapon" % weapon)

    def setPrimaryClip(self, value):
       """ Sets the clip amount for the player's primary weapon or raises KeyError if the player has no primary weapon. """
       weapon = self.getPrimary()
       if weapon is None:
           raise KeyError('Player has no primary weapon')
       self.setClip(weapon, value)

    def setSecondaryClip(self, value):
       """
       Sets the clip amount of the player's secondary weapon or raises KeyError
       if the player has no secondary weapon.
       """
       weapon = self.getSecondary()
       if weapon is None:
           raise KeyError('Player has no secondary weapon')
       self.setClip(weapon, value)

    def setHealth(self, value):
        """ Sets the player's health amount. """
        es.setplayerprop(self.userid, "CBasePlayer.m_iHealth", value)

    def setArmor(self, value):
        """ Sets the player's armor amount. """
        es.setplayerprop(self.userid, "CCSPlayer.m_ArmorValue", value)

    def setSpeed(self, value):
        """ Sets the player's speed multiplier. """
        es.setplayerprop(self.userid, "CBasePlayer.localdata.m_flLaggedMovementValue", value)

    def setCash(self, value):
        """ Sets the player's cash amount. """
        es.setplayerprop(self.userid, "CCSPlayer.m_iAccount", value)

    def setDefuser(self, value):
        """ Set to one to give the player a defuse kit or set to zero to remove the player's defuse kit. """
        es.setplayerprop(self.userid, "CCSPlayer.m_bHasDefuser", value)

    def setNightvision(self, value):
        """ Set to one to give the player a night vision or set to zero to remove the player's night vision. """
        es.setplayerprop(self.userid, "CCSPlayer.m_bHasNightVision", value)

    def setNightvisionState(self, value):
        """ Set to one to toggle the player's night vision on or set to zero to toggle the player's night vision off. """
        es.setplayerprop(self.userid, "CCSPlayer.m_bNightVisionOn", value)

    def setNightvisionOn(self, *a, **kw):
        """ Wraps setNightvisionState """
        self.setNightvisionState(*a, **kw)

    def viewPlayer(self, value):
        """ Sets the player's view to look at another player. """
        self.viewCoord(getPlayer(value).getEyeLocation())

    def viewCoord(self, value):
        """ Sets the player's view to look at a specified coordinate. """
        myLocation  = self.getEyeLocation()
        myVector    = es.createvectorstring(myLocation[0], myLocation[1], myLocation[2])
        theVector   = es.createvectorstring(value[0], value[1], value[2])
        ourVector   = es.createvectorfrompoints(myVector, theVector)
        ourVector   = es.splitvectorstring(ourVector)
        myViewAngle = self.getViewAngle()
        ourAtan = math.degrees(math.atan(float(ourVector[1]) / float(ourVector[0])))
        if float(ourVector[0]) < 0:
            RealAngle = ourAtan + 180
        elif float(ourVector[1]) < 0:
            RealAngle = ourAtan + 360
        else:
            RealAngle = ourAtan
        yAngle = RealAngle
        xAngle = 0 - math.degrees(math.atan(ourVector[2] / math.sqrt(math.pow(float(ourVector[1]), 2) + math.pow(float(ourVector[0]), 2))))
        es.server.cmd('es_xsetang %s %s %s %s' % (self.userid, xAngle, yAngle, myViewAngle[2]))

    def lookAt(self, value):
        """ Set's the player's view to look at either a userid or coordinate. """
        if hasattr(value, '__iter__'):
            self.viewCoord(value)
        else:
            self.viewPlayer(value)

    def _push(self, horiz, vert, vert_override=False):
        """
        Pushes the player along his or her view vector.
        Call without underscore, i.e.: player.push(horiz, vert, vert_override)
        """
        myVector = self.viewVector()
        horzX = float(horiz) * float(myVector[0])
        horzY = float(horiz) * float(myVector[1])
        if str(vert_override) == '0':
            vertZ = float(myVector[2]) * float(vert)
        else:
            vertZ = vert
        myNewVector = es.createvectorstring(horzX, horzY, vertZ)
        es.setplayerprop(self.userid, "CBasePlayer.localdata.m_vecBaseVelocity", myNewVector)

    def setModel(self, value):
        """ Sets the player's model. """
        myModel = value.replace("\\", "/")
        if not myModel.startswith("models/"):
            myModel = "models/" + myModel
        if not myModel.endswith(".mdl"):
            myModel = myModel + ".mdl"
        original_color = self.getColor()
        es.setplayerprop(self.userid, "CBaseEntity.m_nModelIndex", es.precachemodel(myModel))
        self.setColor(*original_color)

    def setColor(self, r, g, b, a=None):
        """ Sets the player's color with RGBA format. The alpha value can be omitted. """
        color = int(r) + (int(g) << 8) + (int(b) << 16)
        if a is None:
            color += self.getColor()[3] << 24
        else:
            color += int(a) << 24
        if color >= 2**31: color -= 2**32
        es.setplayerprop(self.userid, "CBaseEntity.m_nRenderMode", es.getplayerprop(self.userid, "CBaseEntity.m_nRenderMode") | 1)
        es.setplayerprop(self.userid, "CBaseEntity.m_nRenderFX", es.getplayerprop(self.userid, "CBaseEntity.m_nRenderFX") | 256)
        es.setplayerprop(self.userid, "CBaseEntity.m_clrRender", color)

    def _noclip(self, value):
        """ Sets the player's noclip status. Call without underscore, i.e.: player.noclip(value) """
        if isinstance(value, bool):
            value = int(value)
        value = str(value)
        if value == '1':
            es.setplayerprop(self.userid, "CBaseEntity.movetype", '8')
        elif value == '0':
            es.setplayerprop(self.userid, "CBaseEntity.movetype", '2')
        else:
            raise ValueError("'" + value + "' invalid value for noclip")

    def _noblock(self, value):
        """
        Set to one to trigger noblock for the player or set to zero to remove noblock.
        Call without underscore, i.e.: player.noblock(value)
        """
        if isinstance(value, bool):
            value = int(value)
        value = str(value)
        if value == '1':
            es.setplayerprop(self.userid, "CBaseEntity.m_CollisionGroup", '2')
        elif value == '0':
            es.setplayerprop(self.userid, "CBaseEntity.m_CollisionGroup", '5')
        else:
            raise ValueError("'" + value + "' invalid value for noblock")

    def _jetpack(self, value):
        """
        Set to one to trigger jetpack for the player or set to zero to remove jetpack.
        Call without underscore, i.e.: player.jetpack(value)
        """
        if isinstance(value, bool):
            value = int(value)
        value = str(value)
        if value == '1':
            es.setplayerprop(self.userid, "CBaseEntity.movetype", '4')
        elif value == '0':
            es.setplayerprop(self.userid, "CBaseEntity.movetype", '2')
        else:
            raise ValueError("'" + value + "' invalid value for jetpack")

    def _freeze(self, value):
        """
        Set to one to freeze the player or set to zero to unfreeze the player.
        Call without underscore, i.e.: player.freeze(value)
        """
        if isinstance(value, bool):
            value = int(value)
        value = str(value)
        if value == '1':
            es.setplayerprop(self.userid, "CBaseEntity.movetype", '0')
        elif value == '0':
            es.setplayerprop(self.userid, "CBaseEntity.movetype", '2')
        else:
            raise ValueError("'" + value + "' invalid value for freeze")

    def _godmode(self, value):
        """ Set to one to put the player in god mode or set to zero to take normal damage """
        if isinstance(value, bool):
            value = int(value)
        value = str(value)
        if value == '1':
            es.setplayerprop(self.userid, "CBasePlayer.m_lifeState", '0')
        elif value == '0':
            es.setplayerprop(self.userid, "CBasePlayer.m_lifeState", '512')
        else:
            raise ValueError("'" + value + "' invalid value for godmode")

    def setLocation(self, value):
        """ Sets the player's location to a coordinate in a three-element storage type. """
        if len(value) != 3:
            raise ValueError('setLocation takes exactly three values')
        es.server.cmd(('es_xsetpos %s ' % self.userid) + ' '.join(map(str, value)))

    def moveTo(self, value):
        """ Moves the player to be near another player as specified by userid. """
        hisLocation = list(es.getplayerlocation(value))
        hisLocation[0] = hisLocation[0] + 50
        hisLocation[2] = hisLocation[2] + 10
        self.setLocation(hisLocation)

    def _flash(self, alpha, duration):
        """
        Blinds the player as if he or she were hit by a flashbang.
        Call without underscore, i.e.: player.flash(alpha, duration)
        """
        # Reset old value
        es.setplayerprop(self.userid, "CCSPlayer.m_flFlashMaxAlpha", 0)
        es.setplayerprop(self.userid, "CCSPlayer.m_flFlashDuration", 0)
        # Set new value
        es.setplayerprop(self.userid, "CCSPlayer.m_flFlashMaxAlpha", alpha)
        es.setplayerprop(self.userid, "CCSPlayer.m_flFlashDuration", duration)

    def blind(self, *a, **kw):
        """ Wrapper for _flash function. """
        self._flash(*a, **kw)

    def setHE(self, value):
        """ Sets the player's HE grenade count. """
        es.setplayerprop(self.userid, "CBasePlayer.localdata.m_iAmmo.011", value)

    def setFB(self, value):
        """ Sets the player's flashbang count. """
        es.setplayerprop(self.userid, "CBasePlayer.localdata.m_iAmmo.012", value)

    def setSG(self, value):
        """ Sets the player's smoke grenade count. """
        es.setplayerprop(self.userid, "CBasePlayer.localdata.m_iAmmo.013", value)

    def setHelmet(self, value):
        """ Sets whether or not the player has a helmet (1 = yes, 0 = no). """
        es.setplayerprop(self.userid, "CCSPlayer.m_bHasHelmet", value)

    def setWeaponColor(self, r, g, b, a=None):
        """
        Sets the player's active weapon to a color in RGBA format.
        The alpha value can be omitted.
        """
        color  = r + (g << 8) + (b << 16)
        handle = es.getplayerhandle(self.userid)
        if a is None:
            color += self.getWeaponColor()[3] << 24
        else:
            color += a << 24
        if color >= 2**31: color -= 2**32
        index = self.getWeaponIndex(self.getAttribute('weapon'))
        if index:
            es.setindexprop(index, "CBaseEntity.m_nRenderMode", es.getindexprop(index, "CBaseEntity.m_nRenderMode") | 1)
            es.setindexprop(index, "CBaseEntity.m_nRenderFX", es.getindexprop(index, "CBaseEntity.m_nRenderFX") | 256)
            es.setindexprop(index, "CBaseEntity.m_clrRender", color)
        else:
            raise KeyError("Player has no active weapon")

    def _burn(self):
        """ Sets the player on fire. Call without underscore, i.e.: player.burn() """
        es.server.cmd('es_xfire %s !self ignite' % self.userid)

    def _extinguish(self):
        """
        Extinguishes the player if he or she is on fire.
        Call without underscore, i.e.: player.extinguish()
        """
        handle = es.getplayerhandle(self.userid)
        for flame_entity in es.createentitylist("entityflame") :
            if es.getindexprop(flame_entity, 'CEntityFlame.m_hEntAttached') == handle:
                es.setindexprop(flame_entity, 'CEntityFlame.m_flLifetime', 0)
                break


    def set(self, param, value=""):
        """
        Including all parameters from the original playerset (except "add" commands), this function
        takes string parameters for all player information the Player class can alter.
        This is the original method playerlib used to alter information.
        """
        param = str(param).lower()
        # SET AMMO
        if param == "ammo":
            myWeapon = str(value[0])
            if myWeapon in ('1', 'primary'):
                self.setPrimaryAmmo(value[1])
            elif myWeapon in ('2', 'secondary'):
                self.setSecondaryAmmo(value[1])
            else:
                myWeapon = weaponlib.getWeapon(value[0])
                if myWeapon is None:
                    raise ValueError("Player has no '%s' weapon" % value[0])
                self.setAmmo(myWeapon, value[1])
        # SET CLIP
        elif param == "clip":
            myWeapon = str(value[0])
            if myWeapon in ('1', 'primary'):
                self.setPrimaryClip(value[1])
            elif myWeapon in ('2', 'secondary'):
                self.setSecondaryClip(value[1])
            else:
                myWeapon = weaponlib.getWeapon(value[0])
                if myWeapon is None:
                    raise ValueError("Player has no '%s' weapon" % value[0])
                self.setClip(myWeapon, value[1])
        # SET HEALTH
        elif param == "health":
            self.setHealth(value)
        # SET ARMOR
        elif param == "armor":
            self.setArmor(value)
        # SET SPEED
        elif param == "speed":
            self.setSpeed(value)
        # SET CASH
        elif param == "cash":
            self.setCash(value)
        # SET DEFUSER
        elif param == "defuser":
            self.setDefuser(value)
        # SET NIGHTVISION
        elif param == "nightvision":
            self.setNightvision(value)
        # SET NIGHTVISION ON
        elif param in ("nightvisionon", "nightvisionstate"):
            self.setNightvisionState(value)
        # SET VIEWPLAYER
        elif param == "viewplayer":
            if hasattr(value, '__iter__'):
                if isinstance(value, dict):
                    raise ValueError("viewPlayer userid cannot be type 'dict'")
            else:
                value = (value,)
            self.viewPlayer(*value)
        # SET VIEWCOORD
        elif param == "viewcoord":
            self.viewCoord(value)
        # SET LOOKAT
        elif param == 'lookat':
            self.lookAt(value)
        # SET PUSH
        elif param == "push":
            self._push(*value)
        # SET MODEL
        elif param == "model":
            self.setModel(value)
        # SET COLOR
        elif param == "color":
            self.setColor(*value)
        # SET NOCLIP
        elif param == "noclip":
            self._noclip(value)
        # SET NOBLOCK
        elif param == "noblock":
            self._noblock(value)
        # SET JETPACK
        elif param == "jetpack":
            self._jetpack(value)
        # SET FREEZE
        elif param == "freeze":
            self._freeze(value)
        # SET GODMODE
        elif param == "godmode":
            self._godmode(value)
        # SET LOCATION
        elif param == "location":
            self.setLocation(value)
        # SET MOVE TO
        elif param == "moveto":
            self.moveTo(value)
        # SET FLASH ALPHA AND DURATION
        elif param == "flash":
            self._flash(*value)
        # SET HE
        elif param == "he":
            self.setHE(value)
        # SET FB
        elif param == "fb":
            self.setFB(value)
        # SET SG
        elif param == "sg":
            self.setSG(value)
        # SET HASHELMET
        elif param in ("hashelmet", "helmet"):
            self.setHelmet(value)
        # SET WEAPON COLOR
        elif param == "weaponcolor":
            self.setWeaponColor(*list(map(int, value)))
        # SET BURN
        elif param == "burn":
            self._burn()
        # SET EXTINGUISH
        elif param == "extinguish":
            self._extinguish()
        else:
            raise KeyError("Cannot set '%s' info for player" % param)

    def add(self, param, value):
        """
        Including all parameters from the original playerset "add" commands, this function takes string
        parameters for all player information the Player class can alter and are frequently added to.
        This is the original method playerlib used to add to the values of frequently altered information.
        """
        param = str(param).lower()
        # ADD AMMO
        if param == "ammo":
            myWeapon = weaponlib.getWeapon(value[0])
            if myWeapon is None:
                raise ValueError("'%s' is an invalid weapon" % value[0])
            self.setAmmo(myWeapon, self.getAmmo(myWeapon) + int(value[1]))
        # ADD CLIP
        elif param == "clip":
            myWeapon = weaponlib.getWeapon(value[0])
            if myWeapon is None:
                raise ValueError("'%s' is an invalid weapon" % value[0])
            self.setClip(myWeapon, self.getClip(myWeapon) + int(value[1]))
        # ADD HEALTH
        elif param == "health":
            self.setHealth(self.getHealth() + int(value))
        # ADD ARMOR
        elif param == "armor":
            self.setArmor(self.getArmor() + int(value))
        # ADD SPEED
        elif param == "speed":
            self.setSpeed(self.getSpeed() + float(value))
        # ADD CASH
        elif param == "cash":
            self.setCash(self.getCash() + int(value))
        else:
            raise KeyError("Adding player %s is not supported" % param)

    """ Player online functions """

    def getOnline(self):
        return self.isOnline()

    def isOnline(self):
        return es.exists('userid', self.userid)

    """ Player management functions (kick/ban/slay) """

    def kill(self):
        """ Slays the player in this gameframe. """
        es.server.queuecmd('es_xsexec %d kill' % self.userid)

    def slay(self):
        self.kill()

    def kick(self, reason=None):
        """ Kicks the player from the server with an optional reason. """
        if not reason is None:
            # This is very light injection protection.
            # We could do better than just remove them.
            reason = reason.replace(';', '').replace('//', '')
            if reason.count('"') % 2:
                # Uneven number of quotes.
                reason += '"'

            es.server.queuecmd('kickid %d %s' % (self.userid, reason))
        else:
            es.server.queuecmd('kickid ' + str(self.userid))

    def banId(self, time, kick=False, reason=None):
        """ Bans the player from the server by SteamID with an optional kick and reason. """
        if kick and reason is None:
            es.server.queuecmd('banid %d %s kick;writeid' % (time, self.getAttribute('steamid')))
        else:
           es.server.queuecmd('banid %d %s;writeid' % (time, self.getAttribute('steamid')))
           if kick:
               self.kick(reason)

    def banAddr(self, time, kick=False, reason=None):
        """ Bans the player from the server by IP address witn an optional kick and reason. """
        es.server.queuecmd('addip %d %s;writeip' % (time, self.getAttribute('address').split(':')[0]))
        if kick:
            self.kick(reason)

    """ End of Player class """


""" Module functions """

def getPlayer(userid):
    """ Returns an instance of the Player class based on the given userid. """
    try:
        # Why not just use the Player constructor?
        return Player(userid)
    except (UseridError, TypeError) as e:
        raise e

def getPlayerList(filtername=None):
    """ Retrieves a list of Player objects based on the given filter. """
    playerlist = list(map(getPlayer, es.getUseridList()))
    if not filtername is None:
        # added this to get rid of spaces in the filter.
        filtername = filtername.replace(' ', '')
        # use the filtername to lookup from filters dictionary
        # apply this filter to the playerlist
        # I have no idea if this works, I've never tried filter() before
        # playerlist = filter(filters[filtername], playerlist)
        for y in filtername.split(","):
            if not y.startswith(('#', '!')):
               raise KeyError(filtername + ' is not a valid playerlib filter')
            if y.startswith('#'):
               playerlist = list(filter(filters[y[1:]], playerlist))
            else:
               playerlist = [x for x in playerlist if not filters[y[1:]](x)]

    return playerlist

def getUseridList(userspec):
    """ Returns either a list of filtered players or a userid if used with a partial name or exact steamid. """
    if not userspec: return []
    if userspec == "#all":
        return es.getUseridList()
    if userspec[0] in "#!":
        return list(map(int, getPlayerList(userspec)))
    else:
        userid = es.getuserid(userspec)
        if userid == 0: return []
        return [userid]

def nearCoord(coord, distance, filtername=None):
    """
    Returns a list of userids within the distance (specified by the "distance"
    parameter) of the given coordinate.
    """
    x1, y1, z1 = coord
    nearlist = []
    for id in getPlayerList(filtername):
        x2, y2, z2 = es.getplayerlocation(id)
        if ((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) ** 0.5 <= distance:
            nearlist.append(id)
    return nearlist

def uniqueid(userid, *a, **kw):
    """ Wrapper of the _uniqueid function of the Player class. """
    return getPlayer(userid).uniqueid(*a, **kw)

""" Player filters """

def registerPlayerListFilter(filtername, filterfunction):
    """ Registers a player filter for getPlayerList and getUseridList. """
    filters[filtername] = filterfunction

def unregisterPlayerListFilter(filtername):
    """ Unregisters a player filter. """
    if filtername in filters:
        del filters[filtername]

def returnAll(x):
    """ Returns True. """
    return True

def returnTeam0(x):
    """ Returns True if the userid parameter is on team 0 otherwise returns False. """
    return x.getAttribute('teamid') == 0

def returnTeam1(x):
    """ Returns True if the userid parameter is on team 1 otherwise returns False. """
    return x.getAttribute('teamid') == 1

def returnTeam2(x):
    """ Returns True if the userid parameter is on team 2 otherwise returns False. """
    return x.getAttribute('teamid') == 2

def returnTeam3(x):
    """ Returns True if the userid parameter is on team 3 otherwise returns False. """
    return x.getAttribute('teamid') == 3

def returnAlive(x):
    """ Returns True if the userid parameter is alive otherwise returns False. """
    return bool(not x.getAttribute('isdead'))

def returnDead(x):
    """ Returns True if the userid parameter is dead otherwise returns False. """
    return bool(x.getAttribute('isdead'))

def returnHuman(x):
    """ Returns True if the userid parameter is a human otherwise returns False. """
    return bool(not x.getAttribute('isbot') and not x.getAttribute('ishltv'))

def returnBot(x):
    """ Returns True if the userid parameter is a bot otherwise returns False. """
    return bool(x.getAttribute('isbot'))


def _registerDefaultFilters():
    """ Registers default filters. """
    registerPlayerListFilter("all", returnAll)
    registerPlayerListFilter("alive", returnAlive)
    registerPlayerListFilter("dead", returnDead)
    registerPlayerListFilter("human", returnHuman)
    registerPlayerListFilter("bot", returnBot)
    registerPlayerListFilter("un", returnTeam0)
    registerPlayerListFilter("spec", returnTeam1)

    # Try to support the team tags of other games
    if _gamename == 'dod':
        registerPlayerListFilter("a", returnTeam2) # Allies
        registerPlayerListFilter("x", returnTeam3) # Axis
    elif _gamename == 'hl2dm':
        registerPlayerListFilter("r", returnTeam2) # Rebels
        registerPlayerListFilter("c", returnTeam3) # Combine
    elif _gamename == 'tf':
        registerPlayerListFilter("r", returnTeam2) # Red
        registerPlayerListFilter("b", returnTeam3) # Blue
    elif _gamename == 'left4dead':
        registerPlayerListFilter("s", returnTeam2) # Survivor
        registerPlayerListFilter("i", returnTeam3) # Infected

    # These filters should always be present for usability and backwards-compatibility
    registerPlayerListFilter("t", returnTeam2) # Terrorist
    registerPlayerListFilter("ct", returnTeam3) # Counter-terrorist
_registerDefaultFilters()
