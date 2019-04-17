# ./addons/eventscripts/_libs/python/keyfile.py

from collections import deque


class ParseError(Exception): pass # Custom exception we can raise for parsing problems


class Parse(dict):
   def __init__(self, filepath):
      """ This class is specifically for parsing files so it makes sense to initialize it with a file path """
      dict.__init__(self)
      self.setFilePath(filepath)

   def setFilePath(self, filepath):
      """ Sets the file path to the keygroup and parses the file """
      self.filepath = filepath
      self.gatherData()

   def gatherData(self):
      """ Parses the keygroup file into dictionary values """
      # Read file
      f = open(self.filepath)
      lines = f.readlines()
      f.close()

      # Clear existing data
      self.clear()

      # Parse read lines
      levels  = deque([self])
      currentlevel = self
      header  = ''
      linenum = 0
      for line in lines:
         linenum += 1
         linesplit = line.split('"')
         splitlen  = len(linesplit)

         # If our last line was a header this line needs to be an opening bracket
         if header:
            if splitlen == 1 and linesplit[0].strip() == '{':
               newlevel = currentlevel[header] = {}
               levels.append(newlevel)
               currentlevel = newlevel
               header = ''
            else:
               self._clearAndError(f'Header "{header}" on line {linenum - 1} not followed by a block')
         # If we have five splits we have an element and a value
         elif splitlen == 5:
            if linesplit[1] in currentlevel:
               if isinstance(currentlevel[linesplit[1]], list):
                 currentlevel[linesplit[1]].append(linesplit[3])
               else:
                 currentlevel[linesplit[1]] = [currentlevel[linesplit[1]], linesplit[3]]
            else:
               currentlevel[linesplit[1]] = linesplit[3]
         # If we have three splits we have a header
         elif splitlen == 3:
            header = linesplit[1]
         # If we only have a closing bracket we close the group and go down one level
         elif splitlen == 1 and linesplit[0].strip() == '}':
            levels.pop()
            if levels:
               currentlevel = levels[~0]
            else:
               self._clearAndError(f'Too many blocks closed at line {linenum}')
         # Whitespace or commented lines are fine, anything else at this point is an error
         elif splitlen != 1 or (line.strip() and not line.strip().startswith('//')):
            self._clearAndError(f'Line {linenum} format not recognized')

      # If we still have open groups when all lines are parsed that's an error
      if len(levels) > 1:
         self._clearAndError(f'Not all blocks closed ({len(levels) - 1} open at EOF)')

   def _clearAndError(self, message=''):
      """ Internal function: Clears the dictionary and raises a ParseError with the supplied message """
      self.clear()
      raise ParseError(message)

"""
### Creates a list of player names in Mani's clients.txt ###

import es
import keyfile

# Parse clients.txt to a dictionary
client_data = keyfile.Parse(es.ServerVar('eventscripts_gamedir') + '/cfg/mani_admin_plugin/clients.txt')
# Go from the "clients.txt" level to the "players" level
client_data = client_data['clients.txt']['players']
# Loop over every unique player name to create a list of real player names
player_names [client_data[unique_name]['name'] for unique_name in client_data]
"""