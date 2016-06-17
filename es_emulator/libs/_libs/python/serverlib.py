# ./addons/eventscripts/_libs/python/serverlib.py

import socket
import struct
import time


class SourceServerError(Exception): pass


class SourceServer(object):
   """ Class to interact with Source game servers """
   # http://developer.valvesoftware.com/wiki/Source_Server_Query_Library
   S2C_CHALLENGE = '\x41'
   S2A_PLAYER = '\x44'
   S2A_RULES = '\x45'
   S2A_INFO = '\x49'
   A2A_ACK = '\x6A'

   A2S_INFO = '\xFF\xFF\xFF\xFF\x54Source Engine Query'
   A2S_PLAYER = '\xFF\xFF\xFF\xFF\x55'
   A2S_RULES = '\xFF\xFF\xFF\xFF\x56'
   A2S_SERVERQUERY_GETCHALLENGE = '\xFF\xFF\xFF\xFF\x57'
   A2A_PING = '\xFF\xFF\xFF\xFF\x69'

   SERVERDATA_EXECCOMMAND = 2
   SERVERDATA_AUTH = 3
   SERVERDATA_RESPONSE_VALUE = 0
   SERVERDATA_AUTH_RESPONSE = 2

   """ Class functions """
   # http://developer.valvesoftware.com/wiki/Server_Queries

   def __init__(self, network, port, timeout=None):
      try:
         self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      except socket.error as e:
         raise SourceServerError(e.message)

      if not timeout is None:
         self.settimeout(timeout)

      self.tcp.connect((network, port))
      self.udp.connect((network, port))

      self.password = ''

   def settimeout(self, value):
      """ Sets server connection timeout time """
      self.tcp.settimeout(value)
      self.udp.settimeout(value)

   def disconnect(self):
      """ Disconnects from server """
      self.tcp.close()
      self.udp.close()

   def raw_send_tcp(self, data):
      """ Internal function: Sends raw tcp data to the server """
      if data:
         self.tcp.send(data)
      return self.parsePacket(self.tcp.recv(4108))

   def raw_send_udp(self, data):
      """ Internal function: Sends raw udp data to the server """
      if data:
         self.udp.send(data)
      return self.udp.recv(4096)

   """ TCP """

   def setRCONPassword(self, password):
      """ Sets the server RCON password """
      self.password = password

      self.raw_send_tcp(self.packet(self.SERVERDATA_AUTH, password, 1234))
      return self.raw_send_tcp(None)[1] == 1234

   def rcon(self, command):
      """ Sends an RCON command to the server and returns the result """
      # Authenticate
      if not self.setRCONPassword(self.password): raise SourceServerError('Bad RCON password')

      # Send RCON command
      result = list(filter(bool, self.raw_send_tcp(self.packet(self.SERVERDATA_EXECCOMMAND, command, 1))[~0]))
      return result[~0] if result else None

   """ UDP """

   def ping(self):
      """ Returns the server ping in seconds """
      starttime = time.time()
      result = self.raw_send_udp(self.A2A_PING)

      if result.startswith('\xFF\xFF\xFF\xFF') and result[4] == self.A2A_ACK:
         return time.time() - starttime

      raise SourceServerError("Unexpected server response for ping '%s'" % result[4])

   def getChallenge(self):
      """ Internal function: Returns a challenge value for querying the server """
      result = self.raw_send_udp(self.A2S_SERVERQUERY_GETCHALLENGE)
      if result.startswith('\xFF\xFF\xFF\xFF') and result[4] == self.S2C_CHALLENGE:
         return result[5:]

      raise SourceServerError("Unexpected server response for getChallenge '%s'" % result[4])

   def getRules(self):
      """ Returns a dictionary of server rules """
      result = self.raw_send_udp(self.A2S_RULES + self.getChallenge())

      if result.startswith('\xFF\xFF\xFF\xFF') and result[4] == self.S2A_RULES:
         rules = {}
         lines = result[7:].split('\x00')
         for x in range(0, len(lines) - 1, 2):
            rules[lines[x]] = lines[x + 1]

         return rules

      raise SourceServerError("Unexpected server response for getRules '%s'" % result[4])

   def getDetails(self):
      """ Returns a dictionary of server details """
      result = self.raw_send_udp(self.A2S_INFO)

      if result.startswith('\xFF\xFF\xFF\xFF') and result[4] == self.S2A_INFO:
         details = {}
         details['version'] = struct.unpack('<B', result[6])[0]
         lines = result[6:].split('\x00', 4)

         for name in ('server name', 'map', 'game directory', 'game description'):
            details[name] = lines.pop(0)

         line = lines.pop(0)
         (details['appid'], details['number of players'], details['maximum players'], details['number of bots'], details['dedicated'],
            details['os'], details['password'], details['secure']) = struct.unpack('<H3BccBB', line[:9])
         details['game version'] = line[9:].split('\x00')[0]

         return details

      raise SourceServerError("Unexpected server response for getDetails '%s'" % result[4])

   def getPlayers(self):
      """ Returns a dictionary of player information """
      result = self.raw_send_udp(self.A2S_PLAYER + self.getChallenge())

      if result.startswith('\xFF\xFF\xFF\xFF') and result[4] == self.S2A_PLAYER:
         playercount = struct.unpack('<B', result[5])[0]

         index, x = 0, 6
         players = {}
         resultlen = len(result) # So we don't have to re-evaluate len()
         while x < resultlen:
            index = struct.unpack('<B', result[x])[0]
            if index in players:
               x += 5
               continue

            currentplayer = players[index] = {}
            y = result.find('\x00', x + 1)
            if y == -1: raise SourceServerError('Error parsing player information')

            currentplayer['player name'] = result[x + 1:y]
            currentplayer['kills'], currentplayer['time connected'] = struct.unpack('<BB', result[y + 1:y + 3])
            x = y + 4

         return players

      raise SourceServerError("Unexpected server response for getPlayers '%s'" % result[4])

   """ Data format functions """

   @staticmethod
   def packet(command, strings, request):
      """ Internal function: Compiles a raw packet string to send to the server """
      if isinstance(strings, str): strings = (strings,)
      result = struct.pack('<II', request, command) + ''.join([x + '\x00' for x in strings])
      return struct.pack('<I', len(result)) + result

   @staticmethod
   def parsePacket(data):
      """ Internal function: Parses a packet and returns the data in "Lengeth, Request, Command, Strings" order """
      if not data: return None
      return struct.unpack('<3I', data[:12]) + (data[12:].split('\x00'),)

"""
>>> server = SourceServer('127.0.0.1', 27015) # Connect to server (network, port)
>>> server.setRCONPassword('mypassword') # Submit the RCON password
True # Password accepted
>>> server.rcon('es_msg Hello, world') # Send an RCON command
'Hello, world\n' # Server response
>>> server.disconnect() # Disconnect from server
"""
"""
server = SourceServer('127.0.0.1', 27015)


### RCON ###
# To use RCON we must first define our password


# Send rcon password
if server.setRCONPassword('mypassword'):
   print 'Password accepted'
else:
   print 'Password not recognized'


# Now we have access to the server console
server.rcon('es_msg Hello, world') # Send a message to the server


result = server.rcon('echo EventScripts FTW!') # Returns 'EventScripts FTW! \n'
result = server.rcon('status') # Returns the text displayed by the status command


### Server queries ###
# These functions DO NOT require an RCON password


result = server.ping() # Returns the ping of the server in seconds relative to this connection

result = server.getRules() # Returns a dictionary of server rules

result = server.getDetails() # Returns a dictionary of general server information
# version / server name / map / game directory / game description / number of players /
# maximum players / number of bots / dedicated / os / password / secure / game version
# More info: http://developer.valvesoftware.com/wiki/Server_Queries#Source_servers_2

result = server.getPlayers() # Returns a dictionary of players on the server
# player name / kills / time connected
# More info: http://developer.valvesoftware.com/wiki/Server_Queries#Reply_format_4
"""


class MasterServerQuery(object):
   # http://developer.valvesoftware.com/wiki/Master_Server_Query_Protocol
   M2A_SERVER_BATCH = '\x66'

   REGION_US_EAST_COAST = '\x00'
   REGION_US_WEST_COAST = '\x01'
   REGION_SOUTH_AMERICA = '\x02'
   REGION_EUROPE = '\x03'
   REGION_ASIA = '\x04'
   REGION_AUSTRALIA = '\x05'
   REGION_MIDDLE_EAST = '\x06'
   REGION_AFRICA = '\x07'
   REGION_WORLD = '\xFF'

   ZERO_IP = '0.0.0.0:0'

   def __init__(self, network=('hl2master.steampowered.com', 27011)):
      self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.server.connect(network)

   def disconnect(self):
      """ Disconnect from the master server """
      self.server.close()

   def getServerList(self, region=None, server_filter='\x00'):
      """
      Returns a list of active Source servers (ip, port) that fit the region and filter criteria
      Region can be specified by the "REGION_" attributes of the MasterServerQuery class
      Server filters takes the output of getFilterString
      """
      if region is None: region = self.REGION_WORLD
      queryformat = '\x31' + region + '%s' + '\x00' + server_filter + '\x00'
      self.server.send(queryformat % self.ZERO_IP)

      result = []
      ip = ''
      data = self.server.recv(8192)[6:]
      while True:
         for x in range(0, len(data) - 1, 6):
            ip = struct.unpack('>BBBBH', data[x:x + 6])
            if ip == (0, 0, 0, 0, 0): return result

            result.append(('%d.%d.%d.%d' % ip[:4], ip[4]))

         self.server.send(queryformat % ('%d.%d.%d.%d:%d' % ip))
         data = self.server.recv(8192)

   @staticmethod
   def getFilterString(dedicated=False, secure=False, gamedir='', mapname='', linux=False, not_empty=False, not_full=False, proxy=False):
      """ Returns a filter string for filtering query results """
      result = ''
      if dedicated:
         result += '\\type\\d'

      if secure:
         result += '\\secure\\1'

      if gamedir:
         result += '\\gamedir\\' + gamedir

      if mapname:
         result += '\\map\\' + mapname

      if linux:
         result += '\\linux\\1'

      if not_empty:
         result += '\\empty\\1'

      if not_full:
         result += '\\full\\1'

      if proxy:
         result += '\\proxy\\1'

      return result if result else '\x00'

"""
masterserver = MasterServerQuery()

# Returns a list of all Source servers
result = masterserver.getServerList()

# Returns a list of Source servers in Europe
result = masterserver.getServerList(masterserver.REGION_EUROPE)

# Returns a list of dedicated CS Source servers in the eastern US
result = masterserver.getServerList(masterserver.REGION_US_EAST_COAST, masterserver.getFilterString(dedicated=True, gamedir='cstrike'))

masterserver.disconnect() # Disconnect from master server
"""
"""
# This function returns the ES version if the server is running ES otherwise returns None
def isRunningES(ip):
   import socket

   running_es = None
   try:
      network, port = ip
      server = SourceServer(network, port)
      server.settimeout(3) # We don't want to wait forever for servers to respond

      rules = server.getRules()
      if 'eventscripts_ver' in rules:
         running_es = rules['eventscripts_ver']
      server.disconnect()
   except SourceServerError: pass # Ingores general Internet-related exceptions and random server weirdness

   return running_es

masterserver = MasterServerQuery()

# Compile a list of CS Source servers running ES (this operation will probably take quite a while)
fun_servers = filter(isRunningES, masterserver.getServerList(server_filter=masterserver.getFilterString(gamedir='cstrike')))

masterserver.disconnect()
"""