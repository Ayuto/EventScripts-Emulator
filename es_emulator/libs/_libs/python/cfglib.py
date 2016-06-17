# ./addons/eventscripts/_libs/python/cfglib.py

import es
import os.path
from configobj import ConfigObj


class AddonCFG(object):
   """ Class for handling addon .cfg files """

   TYPE_TEXT    = 0
   TYPE_CVAR    = 1
   TYPE_COMMAND = 2

   gamedir = str(es.ServerVar('eventscripts_gamedir')).replace('\\', '/')

   """ Begin AddonCFG """

   def __init__(self, cfgpath, indention=3):
      self.cfgpath   = cfgpath.replace('\\', '/')
      self.indention = indention

      self.cfglist  = []
      self.commands = set()
      self.cvars    = {}

   """ Public functions """

   def text(self, text, comment=True):
      """ Adds the given text to the config """
      if not text.strip(): comment = False
      self.cfglist.append((self.TYPE_TEXT, ('// ' if comment else '') + str(text) + '\n'))

   def cvar(self, name, default, description=''):
      """ Adds the named cvar to the config and returns a ServerVar instance """
      var = self.cvars[name] = (name, default, description)
      self.cfglist.append((self.TYPE_CVAR, var))

      return es.ServerVar(name, default, description)

   def command(self, name):
      """ Designates a place for the named server command in the config """
      self.commands.add(name)

      self.cfglist.append((self.TYPE_COMMAND, name))

   def write(self):
      """ Writes the config to file """
      current_cfg = self._parse()
      indention   = ' ' * self.indention

      cfgfile = open(self.cfgpath, 'w')

      # Write the config to file

      for ltype, data in self.cfglist:
         # Write text
         if ltype == self.TYPE_TEXT:
            cfgfile.write(data)

         # Write cvar
         elif ltype == self.TYPE_CVAR:
            name, default, description = data

            cfgfile.write('\n')
            if description:
               cfgfile.write('// %s\n' % description)

            if name in current_cfg:
               cfgfile.write(indention + current_cfg[name][0] + '\n')
               del current_cfg[name]

            else:
               cfgfile.write(indention + name + ' ' + ('"%s"' if isinstance(default, str) else '%s') % default + '\n')

         # Write server command
         elif ltype == self.TYPE_COMMAND:
            if data in current_cfg:
               cfgfile.write('\n')
               for old_line in current_cfg[data]:
                  cfgfile.write(indention + old_line + '\n')
               del current_cfg[data]

      # Write extraneous commands or variables
      if current_cfg:
         cfgfile.write('\n')
      for name in sorted([x for x in current_cfg if es.exists('variable', x) or es.exists('command', x)]):
         for line in current_cfg[name]:
            cfgfile.write(indention + line + '\n')
         del current_cfg[name]

      # Write unrecognized data
      if current_cfg:
         cfgfile.write('\n')
      for name in sorted(current_cfg): # If we don't sort these names they'll appear in a new order every time the .cfg is created
         for line in current_cfg[name]:
            cfgfile.write('// ' + line + '\n')

      cfgfile.close()

   def execute(self, queuecmd=False):
      """ Executes the config """
      es.mexec('..' + self.cfgpath.replace(self.gamedir, '', 1))

   def getCvars(self):
      """ Returns the cvars dictionary """
      return self.cvars.copy()

   """ Private functions """

   def _parse(self):
      """ Internal function: Parses the config and returns the current settings """
      if not os.path.isfile(self.cfgpath):
         return {}

      cfgfile  = open(self.cfgpath)
      cfglines = list(map(str.strip, cfgfile.readlines()))
      cfgfile.close()

      current_cfg = {}

      for line in cfglines:
         if line.startswith('//') or not line: continue

         name = line.split(' ', 1)[0]
         if name in self.commands or name in self.cvars:
            if not line.count(' '): continue

         if name not in current_cfg:
            current_cfg[name] = []

         if line not in current_cfg[name]:
            current_cfg[name].append(line + ('"' if line.count('"') % 2 else ''))

      return current_cfg

"""
# Example usage:

import cfglib
import es

config = cfglib.AddonCFG(es.getAddonPath("mugmod") + "/mugmod.cfg")

config.text("******************************")
config.text("  MUGMOD SETTINGS")
config.text("******************************")

mattie_mugmod     = config.cvar("mattie_mugmod",     1, "Enable/disable Mattie's MugMod")
mugmod_announce   = config.cvar("mugmod_announce",   1, "Announces MugMod each round.")
mugmod_taunt      = config.cvar("mugmod_taunt",      1, "Taunts the mugging victim with a random message.")
mugmod_sounds     = config.cvar("mugmod_sounds",     1, "Enables kill sounds for MugMod")
mugmod_soundfile  = config.cvar("mugmod_soundfile",  "bot/owned.wav", "Sound played for a mugging if mugmod_sounds is 1")
mugmod_percentage = config.cvar("mugmod_percentage", 100, "Percentage of money stolen during a mugging.")

config.write() # Writes the .cfg to file


def load():
   config.execute() # Executes the .cfg to register changes
"""


class AddonINI(ConfigObj):
   """ Class for handling addon .ini files, mostly for langlib """

   def __init__(self, filename, *a, **kw):
      super(AddonINI, self).__init__(filename, *a, **kw)
      self.unrepr   = True # Allows us to write Python types (mainly for strings)
      self.filepath = filename # We need to know the file path to write the file later
      # But we don't want ConfigObj to write the file so we need to make it think we want a string output
      self.filename = None
      self.order    = []

   """ Comment functions """

   def setInitialComments(self, comment_list):
      """ Sets the comments at the top of the ini file, lists or strings acceptable """
      if isinstance(comment_list, str):
         comment_list = [comment_list,]
      if comment_list and not comment_list[~0]:
         del comment_list[~0]
      self.initial_comment = list(map(self.formatComment, comment_list))

   def setFinalComments(self, comment_list):
      """ Sets the comments at the bottom of the ini file, lists or strings acceptable """
      if isinstance(comment_list, str):
         comment_list = [comment_list,]
      if comment_list and not comment_list[~0]:
         del comment_list[~0]
      self.final_comment = [''] + list(map(self.formatComment, comment_list))


   """ Header functions """

   def addGroup(self, header):
      """ Adds a group (tranlation phrase identifier) to the ini for another phrase for translation """
      self.order.append(header)
      self[header]
      self.comments[header] = ['']

   def delGroup(self, header):
      """ Removes a group from the ini file """
      if header in self:
         del self[header]

   def setGroupComments(self, header, comment_list):
      """ Sets the comments associated with a group, comments acceptable as list or strings """
      if isinstance(comment_list, str):
         comment_list = (comment_list,)
      self.comments[header] = [''] + list(map(self.formatComment, comment_list))


   """ Value functions """

   def addValueToGroup(self, header, identifier, value, overwrite=False):
      """
      Adds an identifier (language abbreviation) and corresponding value (translation) to
      a group. This function will be ignored if the identifier already exists unless
      the overwrite keyword is True.
      """
      if identifier not in self[header] or overwrite:
         self[header][identifier] = value
         return True

      return False

   def delValueFromGroup(self, header, identifier):
      """ Removes an identifier (language abbreviation and corresponding translation) from ini file """
      if identifier in self[header]:
         del self[header][identifier]


   """ Override functions """

   def write(self, outfile=None, **kw):
      """
      Writes contents of the ini to file
      We only override this function so the user doesn't have to provide a file name
      and we can write the file ourselves.
      """
      # Write calls itself again with the section keyword. This is very hacky but should work for now
      if 'section' in kw and len(kw) == 1 and outfile is None:
         return super(AddonINI, self).write(**kw)

      # If a blank line is at the bottom of the initial comments we strip it for aesthetics
      if self.initial_comment and not self.initial_comment[~0]:
         del self.initial_comment[~0]

      # If the user specified a preferred order we enforce that here
      if self.order:
         sort_order = list(reversed(self.order))
         self.sections = sorted(self.sections, key=lambda x: (sort_order.index(x) + 1) if x in sort_order else 0, reverse=True)

      # Normal ConfigObj outfiles use the "wb" mode which isn't Windows-friendly
      if outfile is None:
         f = open(self.filepath, 'w')
         f.write('\n'.join(super(AddonINI, self).write()))
         f.close()
      else:
         outfile.write('\n'.join(super(AddonINI, self).write()))

   def __getitem__(self, item):
      """ If the item to get doesn't exist we initialize it with an empty dictionary """
      if item not in self:
         self[item] = {}
      return super(AddonINI, self).__getitem__(item)

   def __str__(self):
      return self.filename

   def __coerce__(self, other):
      if isinstance(str, other):
         return self.filename, other
      return None


   """ Static methods """

   @staticmethod
   def formatComment(comment):
      comment = comment.strip()
      if comment and not comment.startswith('#'):
         comment = '# ' + comment
      return comment

"""
import cfglib
import es

ini = cfglib.AddonINI(es.getAddonPath('test') + '/languages.ini')

# Set initial and final comments
ini.setInitialComments(['Yay, an initial comment!', 'We belong at the beginning of the .ini'])
ini.setFinalComments("I'm a final comment")

# Add an existing group (only has effect if the group doesn't exist)
ini.addGroup('Welcome')
ini.addValueToGroup('Welcome', 'en', 'Welcome') # Values that already exist are ignored
ini.addValueToGroup('Welcome', 'fr', 'Bienvenue')
ini.addValueToGroup('Welcome', 'ge', 'Willkommen')
ini.setGroupComments('Welcome', 'This group is for the welcome message')

ini.addGroup('to Cabaret')
ini.addValueToGroup('to Cabaret', 'en', 'to Cabaret')
ini.addValueToGroup('to Cabaret', 'fr', 'su Cabaret')
ini.addValueToGroup('to Cabaret', 'ge', 'im Cabaret')

ini.write()

### Can also be used with langlib ###
import langlib

text = langlib.Strings(ini)

### languages.ini output ###

# Yay, an initial comment!
# We belong at the beginning of the .ini

# This header is for the welcome message
[Welcome]
en = 'Welcome'
fr = 'Bienvenue'
ge = 'Willkommen'

[to Cabaret]
en = 'to Cabaret'
fr = 'su Cabaret'
ge = 'im Cabaret'

# I'm a final comment
"""
