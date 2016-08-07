# ./addons/eventscripts/_libs/python/weaponlib/__init__.py

import es
from collections import deque
from configobj import ConfigObj
from path import Path


__all__ = [
 'getGameWeapons',
 'getWeapon',
 'getWeaponList',
 'getWeaponNameList',
 'getIndexList',
 'xgetIndexList',
 'getWeaponIndexList',
 'WeaponManager',
 'NoWeaponManager',
 ]

###

class WeaponManager(object):
   class Weapon(str):
      """ Represents weapons, returning property information and a uniform name """
      def __init__(self, name):
         str.__init__(name)
         self.info_name = name

      def setAttributes(self, basename, ammoprop=None, tags=(), slot=0, clip=0, maxammo=0):
         self.info_basename = basename
         self.info_ammoprop = ammoprop
         self.info_tags     = (tags,) if isinstance(tags, str) else tuple(tags)
         self.info_slot     = slot
         self.info_clip     = clip
         self.info_maxammo  = maxammo

      def __getattr__(self, x):
         try:
            return self.get(x)

         except ValueError:
            raise AttributeError("Weapon instance has no attribute '%s'" % x)

      def __getitem__(self, x):
         try:
            return self.get(x)

         except ValueError:
            raise KeyError("'%s'" % x)

      """ Public functions """

      def get(self, info):
         """ Returns weapon properties """
         if info == 'name':
            return self.info_name

         elif info == 'basename':
            return self.info_basename

         elif info == 'prop':
            return self.info_ammoprop

         elif info == 'tags':
            return self.info_tags

         elif info == 'slot':
            return self.info_slot

         elif info == 'clip':
            return self.info_clip

         elif info == 'maxammo':
            return int(self.info_maxammo)

         elif info == 'indexlist':
            return list(es.getEntityIndexes(self))

         elif info == 'indexiter':
            return iter(es.getEntityIndexes(self))

         raise ValueError("No weapon info '%s'" % info)

   class IndexIter(object):
      """ Unique iterator object to control the creating of weapon index lists """
      def __init__(self, weapons):
         self.weapons = deque(weapons)
         self.indexes = deque()

      def __iter__(self):
         return self

      def __next__(self):
         # If there are no indexes in current the list, we need to create a new list
         while not self.indexes:
            # If we have no more weapons the iteration is complete
            if not self.weapons:
               raise StopIteration
            # Create and save the index list for the next weapon
            self.indexes = deque(self.weapons.popleft().indexiter)

         # Remove and return the first index in the index list
         return self.indexes.popleft()

   """ Begin WeaponManager """

   def __init__(self, prefix, ammoprop, specialnames=None):
      self.weapons = {}
      self.prefix = prefix
      self.ammoprop = ammoprop
      self.specialnames = specialnames or {}

   """ Public functions """

   def getWeapon(self, name):
      """ Returns a Weapon instance if the weapon name is valid otherwise returns None """
      name = self._formatName(name)

      return self.weapons.get(name, None)

   def getWeaponList(self, tag='#all'):
      """
      Returns a list of Weapon instances with the specified tag
      but will also return a single-element list if a weapon name is given instead of tags.
      """
      result = iter(self.weapons.values())

      for t in tag.split(','):
         if str(t).startswith('#'):
            result = [weapon for weapon in result if t[1:] in weapon.tags]

         elif str(t).startswith('!'):
            result = [weapon for weapon in result if t[1:] not in weapon.tags]

         else:
            name = self._formatName(tag)
            result = [weapon for weapon in result if weapon == name]

      return result

   def getWeaponNameList(self, tag='#all'):
      """ Returns the string classnames of the Weapon instances returned by getWeaponList(tag) """
      return list(map(str, self.getWeaponList(tag)))

   def getIndexList(self, tag='#all'):
      """ Compiles and returns a list of all indexes for all Weapon instances returned by getWeaponList(tag) """
      indexlist = []
      for weapon in self.getWeaponList(tag):
         indexlist += weapon.indexlist

      return indexlist

   def xgetIndexList(self, tag='#all'):
      """
      Returns a list of all indexes for all Weapon instances returned by getWeaponList(tag)
      but compiles the lists during iteration.
      """
      return self.IndexIter(self.getWeaponList(tag))

   def getWeaponIndexList(self, tag='#all'):
      """ Returns a list of tuples containing (index, Weapon instance) """
      weaponindexlist = []
      for weapon in self.getWeaponList(tag):
         weaponindexlist += [(index, weapon) for index in weapon.indexlist]

      return weaponindexlist

   """ Private functions """

   def _registerWeapon(self, basename, ammoprop=None, *a, **kw):
      """ Register a weapon and its properties to the weapon database """
      name = self._formatName(basename)

      weapon = self.weapons[name] = self.Weapon(name)
      weapon.setAttributes(basename, self.ammoprop + ammoprop if not ammoprop is None else None, *a, **kw)

   def _formatName(self, name):
      """ Formats the given weapon name to a classname """
      name = str(name).lower()
      if name in self.specialnames:
         name = self.specialnames[name]
      if not name.startswith(self.prefix):
         name = self.prefix + name
      return name

###

class NoWeaponManager(object):
   """ This class fails nicely when any attributes are referenced for playerlib compatibility """
   def __init__(self, gamename):
      self.gamename = gamename

   def __getattr__(self, item):
      raise NotImplementedError('weaponlib does not support game "%s"' % self.gamename)


# Path to the weaponlib ini files
INIPATH = Path(es.ServerVar('eventscripts_addondir')).joinpath('_libs', 'python', 'weaponlib')
   
def getGameWeapons(gamename):
   # If we have no ini to parse, we don't recognize this game
   inifile = INIPATH.joinpath(gamename + '.ini')
   if not inifile.isfile():
      return None

   # Parse the ini
   # Any errors in the ini will be allowed to fail
   ini = ConfigObj(inifile)

   # Create the weapon manager for this game
   settings = ini['settings']
   manager = WeaponManager(settings['prefix'], settings['ammoprop'], ini.get('special names', None))

   # Populate the new WeaponManager with Weapon instances
   weapons = ini['weapons']
   for w in weapons:
      current = weapons[w]
      maxammo = current.get('maxammo', '0')
      if maxammo.isdigit():
         maxammo = int(maxammo)
      else:
         maxammo = es.ServerVar('ammo_' + maxammo + '_max')
      manager._registerWeapon(w, current.get('ammoprop', None), current.get('tags', '').split(','),
       int(current.get('slot', 0)), int(current.get('clip', 0)), maxammo)

   # Return a WeaponManager instance for this game
   return manager

currentgame = getGameWeapons(es.getGameName()) or NoWeaponManager(es.getGameName())

###

def getWeapon(*a, **kw):
   return currentgame.getWeapon(*a, **kw)
getWeapon.__doc__ = WeaponManager.getWeapon.__doc__

def getWeaponList(*a, **kw):
   return currentgame.getWeaponList(*a, **kw)
getWeaponList.__doc__ = WeaponManager.getWeaponList.__doc__

def getWeaponNameList(*a, **kw):
   return currentgame.getWeaponNameList(*a, **kw)
getWeaponNameList.__doc__ = WeaponManager.getWeaponNameList.__doc__

def getIndexList(*a, **kw):
   return currentgame.getIndexList(*a, **kw)
getIndexList.__doc__ = WeaponManager.getIndexList.__doc__

def xgetIndexList(*a, **kw):
   return currentgame.xgetIndexList(*a, **kw)
xgetIndexList.__doc__ = WeaponManager.xgetIndexList.__doc__

def getWeaponIndexList(*a, **kw):
   return currentgame.getWeaponIndexList(*a, **kw)
getWeaponIndexList.__doc__ = WeaponManager.getWeaponIndexList.__doc__


"""
>>> import weaponlib

>>> glock = weaponlib.getWeapon('glock')

# Each method works for all attributes
>>> glock.get('clip')
7
>>> glock['clip']
7
>>> glock.clip
7

# Instances return weapon name when coerced to a string
>>> str(glock)
'weapon_glock'
"""
"""
import weaponlib

# This should work on any game
def player_death(event_var):
   weapon   = weaponlib.getWeapon(event_var['weapon'])
   attacker = int(event_var['attacker'])
   if weapon and attacker:
      # Refil the attacker's ammo to max
      prop    = weapon.prop
      maxammo = weapon.maxammo
      if prop and maxammo:
         es.setplayerprop(attacker, prop, maxammo)

      # Find the attacker's weapon index
      index  = 0
      handle = es.getplayerhandle(attacker)
      for x in weapon.indexlist:
         if es.getindexprop(x, 'CBaseEntity.m_hOwnerEntity') == handle:
            index = x
            break

      es.tell(userid, 'You were killed by ' + event_var['es_attackername'] + ' with the ' + weapon + ' (ent index %s)' % index)
"""
"""
import es
import weaponlib


def round_start(event_var):
   # Remove all idle primary weapons
   for index in weaponlib.getIndexList('#primary'):
      if es.getindexprop(index, 'CBaseEntity.m_hOwnerEntity') == -1:
         es.server.cmd('es_xremove %s' % index)


def item_pickup(event_var):
   userid = int(event_var['userid'])
   handle = es.getplayerhandle(userid)

   # Remove any idle weapons of the type just picked up
   for index in weaponlib.getIndexList(event_var['item']):
      if es.getindexprop(index, 'CBaseEntity.m_hOwnerEntity') == -1:
         es.server.cmd('es_xremove %s' % index)

   # Gather a list of the player's weapons
   myweapons = []
   for weapon in weaponlib.getWeaponList('#all'):
      for index in weapon.indexlist:
         if es.getindexprop(index, 'CBaseEntity.m_hOwnerEntity') == handle:
            myweapons.append(weapon)
            break

   # Show the player his or her weapons sorted by slot
   if myweapons:
      sorted_weapons = sorted(myweapons, key=lambda x: x.slot)
      es.tell(userid, 'Current weapons: ' + ', '.join(map(str, sorted_weapons)))

   else:
      es.tell(userid, 'You have no weapons')


def player_spawn(event_var):
   userid = int(event_var['userid'])
   handle = es.getplayerhandle(userid)

   usp = weaponlib.getWeapon('usp')
   # Loop through all usps to find the one belonging to the player
   for index in usp.indexlist:
      if es.getindexprop(index, 'CBaseEntity.m_hOwnerEntity') == handle:

         # Remove the player's usp
         es.server.cmd('es_xremove %s' % index)

         # Set the player's usp ammo to 0
         es.setplayerprop(userid, usp.prop, 0)

         # Stop looping
         break

   glock = weaponlib.getWeapon('glock')
   # Loop through all glocks to find the one belonging to the player
   for index in glock.indexlist:
      if es.getindexprop(index, 'CBaseEntity.m_hOwnerEntity') == handle:
         # Make the player drop the glock
         es.sexec(userid, 'use weapon_glock')
         es.sexec(userid, 'drop')

         # Set the player's glock ammo to max
         es.setplayerprop(userid, glock.prop, glock.maxammo)

         # Stop looping
         break

   # Loop though each primary weapon and set the player's ammo to the number of bullets in one clip
   for weapon in weaponlib.getWeaponList('#primary'):
      for index in weapon.indexlist:
         if es.getindexprop(index, 'CBaseEntity.m_hOwnerEntity') == handle:
            es.setplayerprop(userid, weapon.prop, weapon.clip)
            return
"""