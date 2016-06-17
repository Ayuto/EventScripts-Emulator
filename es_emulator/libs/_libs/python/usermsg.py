'''usermsg.py

Wrappers around some common usermessages.

Note: for more information on what each function does, check the comment
      inside the function.

Available functions:
 * fade(users, 0 = no fade, 1 = fade out 2 = fade in, time to fadein, hold time, red, green, blue, alpha)
 * shake(users, magnitude, time)
 * motd(users, type, title, msg, [show / hide])
 * hudhint(users, msg)
 * centermsg(users, msg)
 * echo(users, msg)
 * saytext2(users, index, msg, [arg1-4])
 * showVGUIPanel(users, panelname, show / hide, data)

All commands first argument is "users". Users accepts the following formats:
 * #all, #alive, #bot, #human, #dead, etc.
 * userids in a sequence (tuple or list).
 * userid as string or integer.
'''

import es
import playerlib

# Plugin information
info = es.AddonInfo()
info['name'] = "Usermsg EventScripts python library"
info['version'] = "r880"
info['authors'] = "ES development team"
info['url'] = "http://python.eventscripts.com/pages/Usermsg"
info['description'] = "Provides complex usermsg functionality simplified"

def fade(users, type, time, holdTime, red, green, blue, alpha=255):
    '''Fades a players screen.'''
    es.usermsg('create', 'fade', 'Fade')
    es.usermsg('write', 'short', 'fade', time)
    es.usermsg('write', 'short', 'fade', holdTime)
    es.usermsg('write', 'short', 'fade', type)
    es.usermsg('write', 'byte', 'fade', red)
    es.usermsg('write', 'byte', 'fade', green)
    es.usermsg('write', 'byte', 'fade', blue)
    es.usermsg('write', 'byte', 'fade', alpha)

    __sendMessage(users, 'fade')

def shake(users, magnitude, time):
    '''Shakes a players screen.'''
    es.usermsg('create', 'shake', 'Shake')
    es.usermsg('write', 'byte', 'shake', 0)
    es.usermsg('write', 'float', 'shake', magnitude)
    es.usermsg('write', 'float', 'shake', 1.0)
    es.usermsg('write', 'float', 'shake', time)

    __sendMessage(users, 'shake')

def motd(users, type, title, message, visible=True):
    '''Shows an info panel to a player.

    Types available:
        0 = Text
        2 = URL
        3 = File
    '''
    # Create KV data
    data = {'title': title,
            'type': type,
            'msg': message
            }

    # Show panel
    showVGUIPanel(users, 'info', visible, data)

def showVGUIPanel(users, panelName, visible, data={}):
    '''Shows a VGUI panel client-side with the option to set its visibility
    state.

    Available panel names (taken straight from Source SDK):
     * all -- ?
     * active -- ?
     * scores -- Scoreboard
     * overview -- Radar / overview map
     * specgui -- Spectator GUI (top bar when spectator)
     * specmenu -- Spectator Menu (bottom bar when spectator)
     * info -- Info panel (MOTD and the like)
     * nav_progress -- Navigation Build Progress
     * team -- Team selection panel
     * class -- Class selection panel
    '''
    # Create the usermessage
    es.usermsg('create', 'panel', 'VGUIMenu')
    es.usermsg('write', 'string', 'panel', panelName)
    es.usermsg('write', 'byte', 'panel', int(visible))
    es.usermsg('write', 'byte', 'panel', len(data))

    # Write KV data
    for key in data:
        es.usermsg('write', 'string', 'panel', key)
        es.usermsg('write', 'string', 'panel', data[key])

    # Show message
    __sendMessage(users, 'panel')

def hudhint(users, msg):
    '''Shows a hint message on a player.'''
    es.usermsg('create', 'hudhint', 'HintText')
    es.usermsg('write', 'bool', 'hudhint', 0)
    es.usermsg('write', 'string', 'hudhint', msg)

    __sendMessage(users, 'hudhint')

def keyhint(users, msg):
    '''Shows a keyhint message on a player.'''
    es.usermsg('create', 'keyhint', 'KeyHintText')
    es.usermsg('write', 'byte', 'keyhint', 1)
    es.usermsg('write', 'string', 'keyhint', msg)

    __sendMessage(users, 'keyhint')

def centermsg(users, msg):
    '''Shows a message in the center of a players screen.'''
    es.usermsg('create', 'centermsg', 'TextMsg')
    es.usermsg('write', 'byte', 'centermsg', 4)
    es.usermsg('write', 'string', 'centermsg', msg)

    __sendMessage(users, 'centermsg')

def echo(users, msg):
    '''Shows a message in a players console.'''
    es.usermsg('create', 'echo', 'TextMsg')
    es.usermsg('write', 'byte', 'echo', 2)
    es.usermsg('write', 'string', 'echo', msg)

    __sendMessage(users, 'echo')

def saytext2(users, index, msg, arg1=0, arg2=0, arg3=0, arg4=0):
    '''Shows a coloured message in a players chat window.'''
    es.usermsg('create', 'saytext2','SayText2')
    es.usermsg('write', 'byte', 'saytext2', index)
    es.usermsg('write', 'byte', 'saytext2', 1)
    es.usermsg('write', 'string', 'saytext2', msg)
    es.usermsg('write', 'string', 'saytext2', arg1)
    es.usermsg('write', 'string', 'saytext2', arg2)
    es.usermsg('write', 'string', 'saytext2', arg3)
    es.usermsg('write', 'string', 'saytext2', arg4)

    __sendMessage(users, 'saytext2')

def hudmsg(users, msg, channel=0, x=0.5, y=0.5,
           r1=255, g1=255, b1=255, a1=255, r2=255, g2=255, b2=255, a2=255,
           effect=0, fadein=0.1, fadeout=0.1, holdtime=4.0, fxtime=0.0):
    '''Shows a coloured message on a players HUD (not supported on CS:S).

    X and Y are from 0 to 1 to be screen resolution independent, -1 means
    center on each axis.

    Effects:
        0 = Fade in and Fade out
        1 = Flickering Credits
        2 = Write out (Training Room)

    Fadein and Fadeout are the amount of time it takes to fade in and out (per
    character if using effect 2).

    Holdtime is how long the message stays on screen.
    '''
    es.usermsg('create','hudmsg','HudMsg')
    es.usermsg('write','byte','hudmsg', channel & 0xff)
    es.usermsg('write','float', 'hudmsg', x)
    es.usermsg('write','float', 'hudmsg', y)
    es.usermsg('write','byte', 'hudmsg', r1)
    es.usermsg('write','byte', 'hudmsg', g1)
    es.usermsg('write','byte', 'hudmsg', b1)
    es.usermsg('write','byte', 'hudmsg', a1)
    es.usermsg('write','byte', 'hudmsg', r2)
    es.usermsg('write','byte', 'hudmsg', g2)
    es.usermsg('write','byte', 'hudmsg', b2)
    es.usermsg('write','byte', 'hudmsg', a2)
    es.usermsg('write','byte', 'hudmsg', effect)
    es.usermsg('write','float', 'hudmsg', fadein)
    es.usermsg('write','float', 'hudmsg', fadeout)
    es.usermsg('write','float', 'hudmsg', holdtime)
    es.usermsg('write','float', 'hudmsg', fxtime)
    es.usermsg('write','string', 'hudmsg', msg)

    __sendMessage(users, 'hudmsg')

def __sendMessage(users, name):
    # Is a filter
    if str(users)[0] == '#':
        users = playerlib.getUseridList(users)
    # Is not a sequence of userids
    elif not hasattr(users, '__iter__'):
        users = (users,)

    # Loop through players
    for userid in users:
        if es.exists('userid', userid): es.usermsg('send', name, userid)

    # Cleanup
    es.usermsg('delete', name)