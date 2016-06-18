"""
print('ES VM TEST')
import es
import playerlib
import cmdlib

def load():
    print('ES VM test loaded')

def unload():
    print('ES VM test unloaded')

def player_say(ev):
    print('player_activate')
    es.msg('#multi', 'hallo #GREEN%s. #darkgreenasd#lightgreen123#defAultAsdasdasd'% ev['es_userweapon'])

    player = playerlib.getPlayer(ev['userid'])
    print(player.health)
    print(player.noclip)
    player.noclip = not player.noclip
    es.tell(ev['userid'], 'asd')
    es.centertell(ev['userid'], 'hallo!')

def player_activate(ev):
    print('player_activate')

for player in playerlib.getPlayerList('#alive'):
    print(player.name)

def f():
    print('f()')

import gamethread

gamethread.delayed(1, f)

import weaponlib

for weapon in weaponlib.getWeaponList('#pistol'):
    print(weapon.name, weapon.clip)

es.server.echo('echo 123')
"""

import es
import cmdlib
"""
def load():
   # Register a server command to the function myfunc
   cmdlib.registerServerCommand('my_server_command', myfunc, "My command's description")

def myfunc(args):
   print('ARGS', args, [args[0]])
   # If our function is: my_server_command <arg1>
   # We first want to check we have the correct number of arguments
   if len(args) == 1:
      es.msg('You used my server command with the argument: %s' % args[0])
   else:
      es.msg('You used an incorrect number of arguments with my server command (expected 1, got %i)' % len(args))

   # It's important to note in this function we can still use es.getargv, es.getargc, and es.getargs if we want.

def unload():
   # Unregisters the server command so another addon can use it
   cmdlib.unregisterServerCommand('my_server_command')
"""

import popuplib

es.msg('Hallo')

myPopup = popuplib.create('example_popup')
# Now add some content to it
myPopup.addline('Hello world!')
myPopup.addline('You are playing with ES 2.0!')
# Send the popup to everyone on the server
myPopup.send(es.getUseridList())