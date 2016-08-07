"""
es.py

Core EventScripts module that powers much of ES/Python integration.

Documentation for public methods in this module:
http://python.eventscripts.com/pages/es

Minimum compatible ES version: 2.1.1.337
"""
# we want all of the es_C functions inside of 'es' module
from es_C import *

# custom imports
import os
import sys
import traceback
import langlib
import re
import operator

class SourceServer:
  splitcmds = re.compile('(?:"[^\n"]+"|[^;\n"]+)+')
  def insertcmd(self, command):
    ''' Inserts a command at the beginning of Valve's console command queue.
    '''
    InsertServerCommand(command)
    return
  def cmd(self, command):
    ''' Inserts a command at the beginning of Valve's console command queue and
        then forces it to be executed right away.
    '''
    splitter = self.splitcmds.findall(command)
    for cmd in splitter:
        ForceServerCommand(cmd)
    return
  def queuecmd(self, command):
    ''' Appends a command to the end of Valve' console command queue.
    '''
    ServerCommand(command)
    return
  def printmsg(self, msg):
    printmsg(msg)
  def log(self, logstr):
    log(logstr)
    # custom commands to allow es.server.est_respawn(userid)
  class CommandProxy:
    ''' Class to pretend to be a direct access function for console
        commands.
    '''
    def __init__(self, name):
      ''' The name of the console command. Raises an exception if it
          doesn't exist.
      '''
      if exists("command", name):
        self.name = name
      else:
        raise NameError("No command called: %s" % name)
    def __call__(self, *args):
      ''' If the command proxy is invoked, call back.
      '''
      output = self.name
      for arg in args:
        output+=" "
        if isinstance(arg, ServerVar):
          output+=arg.getName
        else:
          output+=str(arg)
      ForceServerCommand(output)
  def __getattr__(self, name):
    try:
      return self.CommandProxy(name)
    except NameError as e:
      raise AttributeError("SourceServer has no command or attribute '%s'" % name)
# instantiate Server class
server = SourceServer()

# intelligent class to wrap entity properties
class EntityProp():
  def __init__(self, index, propname):
    self._propname = propname
    self.index = index
    self._propoffset = getpropoffset(propname)
    self._proptype = getproptype(propname)
  def getVal(self):
    return getentitypropoffset(self.index, self._propoffset, self._proptype)
  def __str__(self):
    return str(self.getVal())
  def __float__(self):
    return float(self.getVal())
  def __int__(self):
    return int(self.getVal())
  def getName(self):
    return self._propname
  def getIndex(self):
    return self.index
  def set(self, value):
    setentitypropoffset(self.index, self._propoffset, self._proptype, value)
    return
  def __lt__(self, other):
    return _compare_value(self, other, operator.lt, (str, int, float))
  def __le__(self, other):
    return _compare_value(self, other, operator.le, (str, int, float))
  def __eq__(self, other):
    return _compare_value(self, other, operator.eq, (str, int, float))
  def __ne__(self, other):
    return _compare_value(self, other, operator.ne, (str, int, float))
  def __ge__(self, other):
    return _compare_value(self, other, operator.ge, (str, int, float))
  def __gt__(self, other):
    return _compare_value(self, other, operator.gt, (str, int, float))

# intelligent class to wrap a specific server variable
class ServerVar():
  def __init__(self, name, defaultvalue=0, description=""):
    self._name = name
    if not exists("variable", name):
      # es.set()
      set(name, defaultvalue, description)
  def __str__(self):
    return getString(self._name)
  def __float__(self):
    return getFloat(self._name)
  def __int__(self):
    return getInt(self._name)
  def __bool__(self):
    return bool(getFloat(self._name))
  def getName(self):
    return self._name
  def set(self, value):
    if (isinstance(value,int)):
      setInt(self._name, value)
    elif (isinstance(value, float)):
      setFloat(self._name, value)
    else:
      setString(self._name, str(value))
    return
  def __lt__(self, other):
    return _compare_value(self, other, operator.lt)
  def __le__(self, other):
    return _compare_value(self, other, operator.le)
  def __eq__(self, other):
    return _compare_value(self, other, operator.eq)
  def __ne__(self, other):
    return _compare_value(self, other, operator.ne)
  def __ge__(self, other):
    return _compare_value(self, other, operator.ge)
  def __gt__(self, other):
    return _compare_value(self, other, operator.gt)
  def copy(self, source):
    sourcevar = source
    if isinstance(source, ServerVar):
      sourcevar = source._name
    copy(self._name, str(sourcevar))
  # extra functionality for fun
  def makepublic(self):
    makepublic(self._name)
  def addFlag(self, flagname):
    flags('add', flagname, self._name)
  def removeFlag(self, flagname):
    flags('remove', flagname, self._name)
  def forcecallbacks(self):
    forcecallbacks(self._name)

class SourceServerVariables:
  def getObject(self, var):
    return ServerVar(var)
  def __getitem__(self, var):
    return self.getObject(var)
  def __setitem__(self, var, value):
    if (type(value) == int):
      setInt(var, value)
    elif (type(value) == str ):
      setString(var, value)
    elif (type(value) == float):
      setFloat(var, value)
    return
# instantiate ServerVariables class
server_var = SourceServerVariables()

class SourceEventVariables:
  def __getitem__(self, var):
    return getEventInfo(var)
event_var = SourceEventVariables()

# default output function
def output(string):
  print(string)

class AddonInfo(dict):
  def __init__(self):
    super(AddonInfo, self).__init__(self)
    self.keylist = ['name', 'version', 'url']
    self.name = "Unknown Addon"
    self.version = "0.0"
    self.url = ""
  def __getattr__(self, s):
    return self[s]
  def __setattr__(self, s, value):
    if s != "keylist" and s not in self.keylist:
      self.keylist.append(s)
    self[s] = value


class AddonManager:
  def __init__(self):
    self.AddonList = []
    self.EventListeners = {}
    self.Blocks = {}
    self.TickListeners = []
    self.SayListeners = []
    self.ClientCommandFilters = []
    self.skipsay = False
  def load(self, addon):
    scriptpath = addon.__dict__['__scriptpath']
    name = addon.__name__
    if name.find(".") >= 0:
      name = name[name.find(".")+1:]
    if (addon not in self.AddonList):
      self.AddonList.append(addon)
      if 'load' in addon.__dict__:
        addon.load()
      if 'enable' in addon.__dict__:
        addon.enable()
      dbgmsg(0 if not "corelib" in scriptpath else 1, "[EventScripts] Loaded %s" % scriptpath)
    else:
      dbgmsg(0, "[EventScripts] %s was already loaded" % scriptpath)
  def unload(self, addon):
    #if addon.__dict__.has_key("disable"):
    #  addon.disable()
    if 'unload' in addon.__dict__:
      addon.unload()
    if (addon in self.AddonList):
      self.AddonList.remove(addon)
    else:
      dbgmsg(0, "[EventScripts] %s was not loaded" % addon.__dict__['__scriptpath'])
  def disable(self, addon):
    # TODO: Make disable work for Python addons
    addon.disable()
  def enable(self, addon):
    # TODO: Make enable work for Python addons
    addon.enable()
  def list(self, outputfunc=output):
    for x in self.AddonList:
      outputfunc("  Name: %s %s\n  Desc: %s\nAuthor: %s\nContact: %s\n\n" % (x.Name, x.Version, x.Description, x.Author, x.Contact))
  # register a listener for a specific event
  def registerForEvent(self, listener, eventname, callback):
    if eventname not in self.EventListeners:
      self.EventListeners[eventname] = {}
    self.EventListeners[eventname][listener] = callback
  # unregister a listener
  def unregisterForEvent(self, listener, eventname):
    if eventname not in self.EventListeners:
      return
    if listener in self.EventListeners[eventname]:
      del self.EventListeners[eventname][listener]
  # triggers an event for all registered listeners
  def triggerEvent(self, eventname):
    if eventname not in self.EventListeners:
      return
    for listener in self.EventListeners[eventname]:
      if 'disable' not in listener.__dict__ or not listener.disabled:
        try:
          self.EventListeners[eventname][listener](event_var)
        except:
          sys.excepthook(*sys.exc_info())
  def hasEvent(self, eventname):
    return 1 if eventname in self.EventListeners else 0
  def tick(self):
      for x in self.TickListeners:
        x()
      return
  def clientCommand(self, userid):
    ''' ES will call this whenever anyone sends a client command.
        All handlers are queried to see if they want to handle it,
        if they eat it, they just return False
    '''
    if not self.ClientCommandFilters:
      return 1
    argv = []
    for i in range(cmdargc()):
      argv.append(cmdargv(i))
    for cmdfilter in self.ClientCommandFilters:
      try:
        response = cmdfilter(userid, argv)
        if not response:
          return 0
      except:
         sys.excepthook(*sys.exc_info())
    return 1
  def registerClientCommandFilter(self, callback):
    if callback not in self.ClientCommandFilters:
      self.ClientCommandFilters.append(callback)
  def unregisterClientCommandFilter(self, callback):
    if callback in self.ClientCommandFilters:
      self.ClientCommandFilters.remove(callback)
    return True
  def sayFilter(self, userid, fulltext, teamonly = False):
    ''' ES will call this whenever anyone says anything!
          Return userid, text, and newteam after your filter is done.
          Return a userid of 0 if you want the text to be eaten and done with.
    '''
    if self.skipsay:
      self.skipsay = False
      return True
    else:
        newuserid = userid
        newtext = fulltext
        newteamonly = teamonly
        for listener in self.SayListeners:
          try:
            newuserid, newtext, newteamonly = listener(newuserid, newtext, newteamonly)
            if not newuserid:
              return False
          except:
            sys.excepthook(*sys.exc_info())
        if newuserid == userid and newtext == fulltext and newteamonly == teamonly:
          return True
        else:
          self.skipsay = True
          if newteamonly:
            sexec(newuserid, "say_team %s" % newtext)
          else:
            sexec(newuserid, "say %s" % newtext)
          return False
  def registerSayFilter(self, callback):
    if callback not in self.SayListeners:
      self.SayListeners.append(callback)
  def unregisterSayFilter(self, callback):
    self.SayListeners.remove(callback)
    return True
  def callBlock(self, blockname):
    # TODO: Shouldn't call blocks for disabled addons
    if blockname not in self.Blocks:
      return
    self.Blocks[blockname]()
  def registerTickListener(self, callback):
    if callback not in self.TickListeners:
      self.TickListeners.append(callback)
    setNumRegistered(len(self.TickListeners))
  def unregisterTickListener(self, callback):
    self.TickListeners.remove(callback)
    setNumRegistered(len(self.TickListeners))
  def registerBlock(self, addonname, blockname, callback):
    self.Blocks[addonname + "/" + blockname] = callback
  def unregisterBlock(self, addonname, blockname):
    if addonname + "/" + blockname not in self.Blocks:
      return
    del self.Blocks[addonname + "/" + blockname]
  def getAddonList(self):
    return self.AddonList
  def getAddonInfo(self, name):
    endname, importname = _getModuleAddonImportName(name)
    for addon in self.getAddonList():
      if addon.__name__ == importname:
        for item in addon.__dict__:
          if isinstance(addon.__dict__[item], AddonInfo):
            return addon.__dict__[item]
        break
    return None

# instantiate AddonManager
addons = AddonManager()

def import_addon(name):
    ''' Returns the module for the addon you specified (if it's loaded)
    '''
    endname, importname = _getModuleAddonImportName(name)
    for addon in addons.getAddonList():
        if addon.__name__ == importname:
            return addon
    raise KeyError("%s is not loaded and cannot be imported." % name)

def _getModuleAddonImportName(modulename):
    endname = modulename[modulename.rfind("/")+1:]
    importname = modulename.replace("/", ".") + "." + endname
    return endname, importname

# es_load:
#   open(r"<script-path>/__init__.py", 'a').close()  # touches the script
#   touch <script>/__init__.py
#   import <script>
#   for each function:
#       put it into a blocklist dictionary
#   pygo <script>.load()
def loadModuleAddon(modulename):
    endname, importname = _getModuleAddonImportName(modulename)
    # need to check for the .py, .pyc, or .pyo file
    checkfile = r"%s/%s/%s.py" % (ServerVar('eventscripts_addondir'), modulename, endname)
    checkfile2 = r"%s/%s/%s.pyc" % (ServerVar('eventscripts_addondir'), modulename, endname)
    checkfile3 = r"%s/%s/%s.pyo" % (ServerVar('eventscripts_addondir'), modulename, endname)
    bPresent = os.path.exists(checkfile) or os.path.exists(checkfile2) or os.path.exists(checkfile3)
    if bPresent:
      try:
        open(r"%s/%s/__init__.py" % (ServerVar('eventscripts_addondir'), modulename), 'a').close()
      except IOError as e:
        dbgmsg(0, "Error: Could not open addon: %s" % modulename)
        dbgmsg(1, "Error Details: %s" % e)
        return 1
      try:
        newaddon = __import__(importname)
        if newaddon in addons.AddonList:
          dbgmsg(0, "Addon %s already loaded." % (modulename))
          return 1
      except ImportError as blah:
          dbgmsg(0, "Can't load addon (%s): %s" % (modulename, blah))
          return 1
      # loop deep so we can import the subsubscript if there is one.
      # Need to recurse down a level for each . in the module name
      # e.g. mymodule.sub1.sub2 needs to loop down to sub2
      for j in importname[importname.find(".")+1:].split("."):
        newaddon = newaddon.__dict__[j]
      for f in newaddon.__dict__:
        # loop through every function and register them as blocks
        # TODO: restrict it to commands with no arguments
        if type(newaddon.__dict__[f]).__name__ == "function":
          # Ignore 'private' blocks as denoted by an underscore prefix
          if f[0:1] != "_":
            # right now all functions are treated as both blocks and events
            addons.registerBlock(modulename, f, newaddon.__dict__[f])
            addons.registerForEvent(newaddon, f, newaddon.__dict__[f])
      newaddon.__dict__['__scriptpath']=modulename
      addons.load(newaddon)
      return 1
    else:
      return 0

def unloadModuleAddon(modulename):
    # test
    dbgmsg(0, "[EventScripts] Unloading %s..." % modulename)
    endname = modulename[modulename.rfind("/")+1:]
    importname = modulename.replace("/", ".") + "." + endname
    if importname in sys.modules.keys():
      # it's loaded get rid of it
      newaddon = __import__(importname)
      for j in importname[importname.find(".")+1:].split("."):
        newaddon = newaddon.__dict__[j]
      addons.unload(newaddon)
      for f in newaddon.__dict__:
        # loop through every function and unregister them as blocks
        if type(newaddon.__dict__[f]).__name__ == "function":
          # Ignore 'private' blocks as denoted by an underscore prefix
          if f[0:1] != "_":
            # right now all functions are treated as both blocks and events
            addons.unregisterBlock(modulename, f)
            addons.unregisterForEvent(newaddon, f)
      del sys.modules[importname]
      dbgmsg(0, "[EventScripts] %s has been unloaded" % modulename)
    else:
      dbgmsg(0, "[EventScripts] %s was not loaded" % modulename)

def printScriptList():
  for script in addons.getAddonList():
    scriptout = "(unknown)"
    enabled = "enabled"
    try:
      scriptout = script.__scriptpath
    except:
      try:
        scriptout = script.__name__
      except:
        try:
          scriptout = script.Name
        except:
          scriptout = "(unknown: " + script.__str__ + ")"
    try:
      if script.enabled:
        enabled = "enabled"
      else:
        enabled = "disabled"
    except:
        pass
    dbgmsg(0, "[EventScripts]   [%8s] %s" % (enabled, scriptout))
    # print out extended information
    try:
      for j in script.info.keylist:
        dbgmsg(0, "[EventScripts]    %8s: %s" % (j, script.info[j]))
    except AttributeError:
      pass

_gamename = str(ServerVar('eventscripts_gamedir')).rsplit(os.sep, 1)[~0]
def getGameName():
   return _gamename

def getAddonPath(addon):
    return "%s/%s" % (ServerVar("eventscripts_addondir"), addon)

def local_language():
    ''' Returns the server's local language abbreviation
    '''
    return langlib.getLangAbbreviation(str(ServerVar("eventscripts_language")))

def _compare_value(self, other, comparison, _types=(str, int, float, bool)):
  for type_ in _types:
    if isinstance(other, type_):
      return comparison(type_(self), other)
  return False

# initialize the language libraries
langlib.loadLanguages("%s/_libs/python/deflangs.ini" % ServerVar("eventscripts_addondir"))
langlib.setDefaultLangCallback(local_language)

############################################
# Backwards compatibility patching section
############################################
#replace menu definitions since showMenu works better from Python than es.menu()
_esshell_menu = menu
menu = showMenu

dbgmsg(1,"[EventScripts] es.py loaded.")
