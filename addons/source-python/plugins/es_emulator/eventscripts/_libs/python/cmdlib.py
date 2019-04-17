# ./addons/eventscripts/_libs/python/cmdlib.py

import es
import services

import collections


""" Command manager """


class CMDManager(object):
   class CMDArgs(list):
      """
      Class based on list used to return es.getargv values
      When cast to a string it returns es.getargs
      """
      def __str__(self):
         return es.getargs()

   def __init__(self):
      self.server_commands = {}
      self.say_commands    = {}
      self.client_commands = {}

      self.ex_server_commands = set()

   """ Server commands """

   def registerServerCommand(self, name, callback, description, skipcheck=False):
      """ Registeres a server command to a callback function """
      self._validateCallback(callback)

      name = str(name)
      if name not in self.ex_server_commands:
         if es.exists('variable', name) or (not skipcheck and es.exists('command', name)):
            raise NameError(f"'{name}' is in use as a server command or variable")
         es.regcmd(name, '_cmdlib/server', description)

      self.server_commands[name] = Command(name, callback)
      if name in self.ex_server_commands:
         self.ex_server_commands.remove(name)

   def unregisterServerCommand(self, name):
      """ Unregisteres a server command """
      name = str(name)
      if name in self.server_commands:
         self.ex_server_commands.add(name)
         del self.server_commands[name]

   """ Say commands """

   def registerSayCommand(self, name, callback, description, auth_capability=None, auth_recommendedlevel=None, auth_fail_callback=None):
      """ Registers a say command to the callback function with the option of authorization services """
      self._validateAuthCapability(name, auth_capability, auth_recommendedlevel, 'say')

      self._validateCallback(callback)
      if not auth_fail_callback is None:
         self._validateCallback(auth_fail_callback)

      name = str(name).lower()
      if es.exists('saycommand', name): raise NameError(f"'{name}' is in use as a say command")

      es.regsaycmd(name, '_cmdlib/say', description)
      cmd = self.say_commands[name] = PlayerCommand(name, callback)

      if not auth_capability is None and not auth_recommendedlevel is None:
         cmd.setPermission(auth_capability, permissionToInteger(auth_recommendedlevel), auth_fail_callback)

   def unregisterSayCommand(self, name):
      """ Unregisters a say command """
      name = str(name).lower()
      if name in self.say_commands:
         es.unregsaycmd(name)
         del self.say_commands[name]

   """ Client commands """

   def registerClientCommand(self, name, callback, description, auth_capability=None, auth_recommendedlevel=None, auth_fail_callback=None):
      """ Registers a client command to the callback function with the option of authorization services """
      self._validateAuthCapability(name, auth_capability, auth_recommendedlevel, 'client')

      self._validateCallback(callback)
      if not auth_fail_callback is None:
         self._validateCallback(auth_fail_callback)

      name = str(name).lower()
      if es.exists('clientcommand', name): raise NameError(f"'{name}' is in use as a client command")

      es.regclientcmd(name, '_cmdlib/client', description)
      cmd = self.client_commands[name] = PlayerCommand(name, callback)

      if not auth_capability is None and not auth_recommendedlevel is None:
         cmd.setPermission(auth_capability, permissionToInteger(auth_recommendedlevel), auth_fail_callback)

   def unregisterClientCommand(self, name):
      """ Unregisters a client command """
      name = str(name).lower()
      if name in self.client_commands:
         es.unregclientcmd(name)
         del self.client_commands[name]

   """ Miscellaneous """

   def callback(self, cmdlist, name):
      """
      This function is called when a server, say, or client command is received
      If the command name is present in the list of the same type of commands, the callback function is called
      """
      if name in cmdlist:
         cmdlist[name].execute(self.CMDArgs(es.getargv(x) for x in range(1, es.getargc())))

   @staticmethod
   def _validateCallback(callback):
      """
      If the callback is not a string or callable function we
      call the callback to raise an error
      """
      if not isinstance(callback, collections.Callable) and not isinstance(callback, str):
         callback()

   @staticmethod
   def _validateAuthCapability(name, auth_capability, auth_recommendedlevel, command_type):
      """
      Raises an error if only one auth argument is provided or both arguments
      are provided but there is no available authorization service
      """
      if auth_capability is None and not auth_recommendedlevel is None:
         raise ValueError('auth_capability is required when auth_recommendedlevel is provided')
      elif not auth_capability is None and auth_recommendedlevel is None:
         raise ValueError('auth_recommendedlevel is required when auth_capability is provided')
      elif not auth_capability is None and not auth_recommendedlevel is None:
         if not services.isRegistered('auth'):
            raise KeyError(f"Cannot register {command_type} command '{name}' as no authorization service is loaded")

cmd_manager = CMDManager()

### Register/unregister wrappers ###

def registerServerCommand(*a, **kw):
   cmd_manager.registerServerCommand(*a, **kw)
registerServerCommand.__doc__ = CMDManager.registerServerCommand.__doc__

def unregisterServerCommand(*a, **kw):
   cmd_manager.unregisterServerCommand(*a, **kw)
unregisterServerCommand.__doc__ = CMDManager.unregisterServerCommand.__doc__

def registerSayCommand(*a, **kw):
   cmd_manager.registerSayCommand(*a, **kw)
registerSayCommand.__doc__ = CMDManager.registerSayCommand.__doc__

def unregisterSayCommand(*a, **kw):
   cmd_manager.unregisterSayCommand(*a, **kw)
unregisterSayCommand.__doc__ = CMDManager.unregisterSayCommand.__doc__

def registerClientCommand(*a, **kw):
   cmd_manager.registerClientCommand(*a, **kw)
registerClientCommand.__doc__ = CMDManager.registerClientCommand.__doc__

def unregisterClientCommand(*a, **kw):
   cmd_manager.unregisterClientCommand(*a, **kw)
unregisterClientCommand.__doc__ = CMDManager.unregisterClientCommand.__doc__

### Command callbacks ###

def callbackServer():
   """
   Called when a server command is used, this function gives a list of
   current server commands and the server command used to cmd_manager.callback,
   which in turn decides a function should be executed.
   """
   cmd_manager.callback(cmd_manager.server_commands, es.getargv(0))
es.addons.registerBlock('_cmdlib', 'server', callbackServer)

def callbackSay():
   """
   Called when a say command is used, this function gives a list of
   current say commands and the say command used to cmd_manager.callback,
   which in turn decides a function should be executed.
   """
   cmd_manager.callback(cmd_manager.say_commands, es.getargv(0).lower())
es.addons.registerBlock('_cmdlib', 'say', callbackSay)

def callbackClient():
   """
   Called when a client command is used, this function gives a list of
   current client commands and the client command used to cmd_manager.callback,
   which in turn decides a function should be executed.
   """
   cmd_manager.callback(cmd_manager.client_commands, es.getargv(0).lower())
es.addons.registerBlock('_cmdlib', 'client', callbackClient)


""" Command classes """


class Command(object):
   """ This class stores the name and callback function of a server command """
   def __init__(self, name, callback):
      self.name     = name
      self.callback = callback

   def execute(self, args):
      """ When told to execute a function we only need to pass the command's arguments """
      if isinstance(self.callback, collections.Callable):
         self.callback(args)
      else:
         es.doblock(self.callback)


class PlayerCommand(Command):
   """
   This class stores the name and callback functions of say or client commands
   It authorizes player as needed before function execution
   """
   auth_capability    = None
   auth_fail_callback = None

   def execute(self, args):
      """
      When told to execute the function we need to pass the userid of the player who used the command
      as well as the command's arguments. We also need to determine if the player is authorized to
      use the command.
      """
      userid = es.getcmduserid()
      # No auth? No fuss.
      if not self.auth_capability is None:
         # Check whether the userid is authorized
         is_authed = services.use('auth').isUseridAuthorized(userid, self.auth_capability)
         if not is_authed:
            # If a callback has been specified for auth failure then execute that function
            if self.auth_fail_callback:
               if isinstance(self.auth_fail_callback, collections.Callable):
                  self.auth_fail_callback(userid, args)
               else:
                  es.doblock(self.auth_fail_callback)
            # We have yet to inform the player they aren't authorized so we need to do it
            else:
               es.tell(userid, 'You are not authorized to use the ' + self.name + ' command.')
            return

      if isinstance(self.callback, collections.Callable):
         self.callback(userid, args)
      else:
         es.server.queuecmd('es_xdoblock ' + self.callback)

   def setPermission(self, auth_capability, auth_recommendedlevel, auth_fail_callback=None):
      """ Sets permission information for say or client commands """
      services.use('auth').registerCapability(auth_capability, auth_recommendedlevel)
      self.auth_capability    = auth_capability
      self.auth_fail_callback = auth_fail_callback


""" Helper function for this and other modules """

def permissionToInteger(permission):
   """
   Converts a text permission level ('ROOT', 'ADMIN', etc) to its
   integer equivalent
   """
   if isinstance(permission, int):
      return permission
   value = services.use('auth').__getattribute__(permission)
   if isinstance(value, int):
      return value
   raise NameError(f"'{permission}' is not a valid auth permission")


""" Examples """

""" # Server command example
import cmdlib
import es

def load():
   # Register a server command to the function myfunc
   cmdlib.registerServerCommand('my_server_command', myfunc, "My command's description")

def myfunc(args):
   # If our function is: my_server_command <arg1>
   # We first want to check we have the correct number of arguments
   if len(args) == 1:
      es.msg('You used my server command with the argument: %s' % args[0])
   else:
      es.msg('You used an incorrect number of arguments with my server command (expected 1, got %i)' % len(args))

   # It's important to note in this function we can still use es.getargv, es.getargc, and es.getargs if we want.

def unload():
   # Unregisters the server command so another addon can use it
   cmdlib.unregisterServerCommand('my_server_command')"""


""" # Say command anyone can execute
import cmdlib
import es

def load():
   # Register a say command to the function mysaycmd
   cmdlib.registerSayCommand('broadcast', mysaycmd, 'Allows players to broadcast a message with es_centermsg')

def mysaycmd(userid, args):
   # It makes more sense here to use the entire string of parameters than each argument individually.
   # This also preserves quotation marks in the parameters.
   es.centermsg('%s: %s' % (es.getplayername(userid), str(args)))

def unload():
   # Unregister the say command as is normally done
   cmdlib.unregisterSayCommand('broadcast') """


""" # Say command only authorized players can execute
import cmdlib
import es

def load():
   # Register a say command to the function mysaycmd with the 'use_broadcast' permission
   # If at this point an auth provider is not loaded the following line will error.
   cmdlib.registerSayCommand('broadcast', mysaycmd, 'Allows players to broadcast a message with es_centermsg', 'use_broadcast', 'ADMIN', mysaycmd_noauth)
   # Possible values for auth_recommendedlevel include (as strings): ROOT, ADMIN, POWERUSER, IDENTIFIED, UNRESTRICTED
   # The callback for non-authorized clients can be omitted.

def mysaycmd(userid, args):
   # It makes more sense here to use the entire string of parameters than each argument individually.
   # This also preservers quotation marks in the parameters.
   es.centermsg('%s: %s' % (es.getplayername(userid), str(args)))

def mysaycmd_noauth(userid, args):
   # This client is not authorized
   es.tell(userid, 'You are not authorized to use the broadcast command')

def unload():
   # Unregister the say command as is normally done
   cmdlib.unregisterSayCommand('broadcast') """

""" # Client commands work much the same as say commands only they use:
# cmdlib.registerClientCommand
# cmdlib.unregisterClientCommand """