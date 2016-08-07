# ./addons/eventscripts/corelib/clientcmd/clientcmd.py

import cmdlib
import es


""" Main clientcmd function """

def clientcmd_cmd(args):
   """ Provides an easy way to create client or say commands that require authorization to use """
   if len(args) > 1:
      arg0 = args[0].lower()
      # Creating commands
      if arg0 == 'create':
         if len(args) == 6:
            arg1 = args[1].lower()
            if arg1 in ('say', 'console'):
               permission = args[5].lower()
               if permission in flags:
                  if arg1 == 'say':
                     cmdlib.registerSayCommand(args[2].lower(), args[3], 'Permission-based say command', args[4], flags[permission])
                  else:
                     cmdlib.registerClientCommand(args[2].lower(), args[3], 'Permission-based client console command', args[4], flags[permission])
               else:
                  # Sort flags for output from most restricted to least restricted
                  sorted_flags = ', '.join(sorted(flags, key=lambda x: cmdlib.permissionToInteger(flags[x])))
                  es.dbgmsg(0, '"' + permission + '" is an invalid permission flag for clientcmd.\nAcceptable flags are: ' + sorted_flags)
            else:
               es.dbgmsg(0, 'Second parameter of clientcmd must be "say" or "console"')
         else:
            es.dbgmsg(0, 'Incorrect number of parameters given to clientcmd create (expected 6, got %s)\nSyntax: clientcmd create <say/console> <command name> <block to call> <capability name> <permission level>' % len(args))

      # Deleting commands
      elif arg0 == 'delete':
         if len(args) == 3:
            arg1 = args[1].lower()
            if arg1 == 'say':
               cmdlib.unregisterSayCommand(args[2])
            elif arg1 == 'console':
               cmdlib.unregisterClientCommand(args[2])
            else:
               es.dbgmsg(0, 'Second parameter of clientcmd must be "say" or "console"')
         else:
            es.dbgmsg(0, 'Incorrect number of parameters given to clientcmd delete (expected 3, got %s)\nSyntax: clientcmd delete <say/console> <command name>' % len(args))
      else:
         es.dbgmsg(0, 'First parameter of clientcmd must be "create" or "delete"')
   else:
      es.dbgmsg(0, 'clientcmd must have "create" or "delete" as the first argument and "say" or "console" as the second')

cmdlib.registerServerCommand('clientcmd', clientcmd_cmd, 'Provides an easy way to create client or say commands that require authorization to use')


""" Dictionay for converting flags to permissions """

flags = {'#root':'ROOT',
'#admin':'ADMIN',
'#poweruser':'POWERUSER',
'#known':'IDENTIFIED',
'#all':'UNRESTRICTED'}


"""// ./addons/eventscripts/myaddon/es_myaddon.txt
// Say command only authorized players can execute

block load()
{
   // Register a say command to the block mysaycmd with the 'use_broadcast' capability
   // If at this point an auth provider is not loaded the following line will error.
   // This works similar to es_regsaycmd only it allows capabilities/permissions
   clientcmd create say broadcast "myaddon/mysaycmd" "use_broadcast" #admin
   // Possible values for the recommend level include: #root, #admin, #poweruser, #known, #all
}

block mysaycmd
{
   // The user must be authorized so let's display the text
   es_set myaddon_userid 0
   es_set myaddon_username 0
   es_set myaddon_broadcast 0

   // Get the player's name
   es_getcmduserid myaddon_userid
   es_getplayername myaddon_username server_var(myaddon_userid)

   // Get the text to broadcast
   es_getargs myaddon_broadcast

   // Format the text to broadcast to include the player's name
   es_formatv myaddon_broadcast "%1: %2" myaddon_username myaddon_broadcast

   // Broadcast the message
   es_centermsg server_var(myaddon_broadcast)
}

block unload
{
   // Now we delete the say command since we are done with it
   // This works similar to es_unregsaycmd
   clientcmd delete say broadcast
}"""
"""// Console commands work much the same way only they use:
clientcmd create console <command name> <block to call> <capability name> <permission level>
clietncmd delete console <command name>"""