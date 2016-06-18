# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
#   Memory
import memory
#   Cvars
from cvars import cvar
from cvars import ConVar
from cvars.flags import ConVarFlags
#   Commands
from commands import Command
from commands.say import SayCommandGenerator
from commands.say import get_say_command
from commands.client import ClientCommandGenerator
from commands.client import get_client_command
from commands.server import get_server_command
#   Engines
from engines.server import engine_server
from engines.server import global_vars
from engines.server import server_game_dll
#   Events
from events.manager import game_event_manager
#   Messages
from messages import TextMsg
from messages import SayText2
from messages import ShowMenu
#   Players
from players.entity import Player
from players.helpers import index_from_userid
from players.helpers import userid_from_edict
from players.helpers import edict_from_userid
from players.voice import voice_server
#   Entities
from entities.entity import BaseEntity
from entities.helpers import inthandle_from_index
from entities.helpers import index_from_inthandle
from entities.helpers import edict_from_index
from entities.helpers import pointer_from_index
from entities.props import SendPropType
#   Filters
from filters.players import PlayerIter
#   Listeners
from listeners.tick import Delay
#   Mathlib
from mathlib import QAngle
from mathlib import Vector

# ES Emulator
#   Logic
from es_emulator.logic import current_event_vars
from es_emulator.logic import server_command_proxies
from es_emulator.logic import say_command_proxies
from es_emulator.logic import client_command_proxies
from es_emulator.logic import command_info
#   Helpers
from es_emulator.helpers import _prepare_msg
from es_emulator.helpers import _get_prop_info
from es_emulator.helpers import atoi
from es_emulator.helpers import atof
from es_emulator.helpers import _cexec
from es_emulator.helpers import _is_dead
from es_emulator.helpers import _get_send_prop_type_name
from es_emulator.helpers import _get_convar_flag
from es_emulator.helpers import _get_menu_options


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# Helper variable for es.event()
_current_event = None


# =============================================================================
# >> ES FUNCTIONS
# =============================================================================
def ForceServerCommand(command_str):
    """Inserts a command to the server queue at the beginning and forces execution."""
    c = Command()
    if not c.tokenize(command_str):
        return 1

    command = cvar.find_command(c[0])
    if command:
        if command.is_command():
            # TODO: This is not the equivalent. Call command.dispatch(c) instead
            engine_server.server_command(c.arg_string)
            engine_server.server_execute()
    else:
        convar = cvar.find_var(c[0])
        if convar:
            convar.set_string(c.arg_string)
        else:
            engine_server.insert_server_command(command_str)

    return 1

def InsertServerCommand(command_str):
    """Inserts a command to the server queue at the beginning."""
    engine_server.insert_server_command(command_str)
    return 1

def ServerCommand(command_str):
    """Adds a command to the end of the server queue."""
    engine_server.server_command('wait;{}'.format(command_str))
    return 1

def _disable(*args):
    """EventScripts internal command."""
    raise NotImplementedError

def _foreachkey(*args):
    """EXPERIMENTAL. Loops through a keygroup and performs a single command on each key, providing a single variable with the key name."""
    raise NotImplementedError

def _foreachval(*args):
    """EXPERIMENTAL. Loops through a keygroup and performs a single command on each key, providing a single variable with the key name."""
    raise NotImplementedError

def _unload(*args):
    """EventScripts internal command."""
    raise NotImplementedError

def botsetvalue(userid, convar, value):
    """Sets a convar value for a fake client."""
    try:
        edict = edict_from_userid(atoi(userid))
    except ValueError:
        dbgmsg(0, 'SetFakeClientConvarValue: Unable to find player')
    else:
        engine_server.set_fake_client_convar_value(edict, convar, str(value))

def centermsg(msg):
    """Broadcasts a centered HUD message to all players."""
    TextMsg(msg).send()

def centertell(userid, msg):
    """Sends a centered HUD message to all players."""
    userid = atoi(userid)
    if userid > 0:
        try:
            index = index_from_userid(userid)
        except ValueError:
            return

        TextMsg(msg).send(index)
    else:
        centermsg(msg)

def cexec(userid, command_str):
    """Forces a userid to execute a command in their console."""
    try:
        player = Player.from_userid(atoi(userid))
    except ValueError:
        return

    _cexec(player, command_str)

def cexec_all(command_str):
    """Forces all users to execute a command in their console."""
    for player in PlayerIter():
        _cexec(player, command_str)

def changeteam(userid, team):
    """Changes the team of the player."""
    userid = atoi(userid)
    try:
        player = Player.from_userid(userid)
    except ValueError:
        dbgmsg(0, 'Player doesn\'t exist: {}'.format(userid))
        return

    player.team = atoi(team)

def cmdargc():
    """Gets the command parameter count passed to the current Valve console command."""
    command_info.argc

def cmdargs():
    """Gets the commandstring passed to the current Valve console command."""
    command_info.args

def cmdargv(index):
    """Gets the command parameter passed to the current Valve console command."""
    command_info.get_argv(index)

def commandv(name):
    """Just runs a command-string inside of the variable."""
    convar = cvar.find_var(name)
    if convar:
        engine_server.insert_server_command(convar.get_string())

def copy(var1_name, var2_name):
    """Reads the server variable referenced by varname2 and copies it into the variable referenced by varname."""
    var1 = cvar.find_var(var1_name)
    var2 = cvar.find_var(var2_name)
    var1.set_string(var2.get_string())

def createbot(name):
    """Adds a bot to the server."""
    return userid_from_edict(engine_server.create_fake_client(name))

def createentity(classname, targetname=''):
    """Creates an entity somewhere by name."""
    entity = BaseEntity.create(classname)
    if targetname:
        entity.set_key_value_string('targetname', targetname)

    return entity.index

def createentityindexlist(classname=None):
    """Creates a keygroup (or dictionary) of all indexes for an entity class or for all entities."""
    # TODO: Validate if this is the correct structure
    result = {}
    for entity in EntityIter(classname):
        result[entity.index] = entity.classname

    return result

def createentitylist(classname=None):
    """Creates a keygroup (or dictionary) for an entity class or for all entities."""
    result = {}
    for entity in EntityIter(classname):
        temp = result[entity.index] = {}
        temp['classname'] = entity.classname
        temp['handle'] = entity.inthandle
        # TODO: Add a full server class dump

    return result

def createplayerlist(userid=None):
    """Creates a new keygroup containing the current list of players."""
    if userid is None:
        players = PlayerIter()
    else:
        players = [Player.from_userid(atoi(userid))]

    result = {}
    for player in players:
        temp = result[player.userid] = {}
        temp['name'] = player.name
        temp['steamid'] = player.steamid
        temp['index'] = player.index
        temp['teamid'] = player.team
        temp['kills'] = player.kills
        temp['deaths'] = player.deaths
        temp['armor'] = player.armor
        temp['model'] = player.model_name
        temp['isdead'] = _is_dead(player)
        temp['isbot'] = player.is_fake_client()
        temp['ishltv'] = player.is_hltv()
        temp['isobserver'] = player.is_observer()
        temp['isinavehicle'] = player.is_in_a_vehicle()
        temp['health'] = player.health
        temp['serialnumber'] = player.edict.serial_number
        temp['weapon'] = player.playerinfo.weapon_name
        temp['handle'] = player.inthandle

        info = engine_server.get_player_net_info(player.index)
        if info is not None:
            # TODO: ES does some calculations for ping and packetloss
            temp['ping'] = 0
            temp['packetloss'] = 0
            temp['timeconnected'] = info.time_connected
        else:
            # Bots
            temp['ping'] = 0
            temp['packetloss'] = 0

        temp['address'] = player.address

        origin = player.origin
        temp['x'] = origin.x
        temp['y'] = origin.y
        temp['z'] = origin.z
        temp['language'] = player.language

    return result

def createscriptlist(scriptname=None):
    """Creates a new keygroup containing the current list of players."""
    raise NotImplementedError

def createvectorfrompoints(a, b):
    """Creates a vector-string that goes from point/vector A to point/vector B."""
    raise NotImplementedError

def createvectorstring(x, y, z):
    """Creates a string form of three x y z variables representing a vector."""
    return '{},{},{}'.format(x, y, z)

def dbgmsg(level, msg):
    """Outputs a message to the console."""
    # TODO: Create a proper implementation
    print(msg)

def dbgmsgv(level, convar_name):
    """Prints a debug message for EventScripts"""
    convar = cvar.find_var(convar_name)
    if convar is not None:
        dbgmsg(level, convar.get_string())
    else:
        dbgmsg(0, 'ERROR: variable {} does not exist.'.format(convar_name))

def delayed(delay, commandstring):
    """Will run <commandstring>, after <seconds> seconds."""
    Delay(delay, engine_server.server_command, commandstring)

def disable(*args):
    """Disables a script that has been loaded."""
    raise NotImplementedError

def doblock(blockname):
    """Executes a block."""
    import es
    es.addons.callBlock(blockname)

def dosql(*args):
    """Does some SQL."""
    raise NotImplementedError

def dumpconcommandbase():
    """Outputs all the console commands and variables."""
    command_count = 0
    convar_count = 0
    current = cvar.commands
    while current:
        if current.is_command():
            type_str = 'CMD'
            command_count += 1
        else:
            type_str = 'VAR'
            convar_count += 1

        print('{}: {}\n\t{}'.format(type_str, current.name, current.help_text))
        current = current.next

    print('Total: {}\tCommands: {}\tVariables: {}'.format(
        command_count+convar_count, command_count, convar_count))

def dumpentities(*args):
    """Dumps to console all server classes and properties for all entities."""
    raise NotImplementedError

def dumpserverclasses():
    """Dumps to the console all server classes."""
    current = server_game_dll.all_server_classes
    while current:
        table = current.table

        # TODO: Get m_InstanceBaselineIndex
        m_InstanceBaselineIndex = 0

        print('{} {} ({} properties)'.format(
            current.name, m_InstanceBaselineIndex, table.length))

        for prop in table:
            print('---------{} : {}'.format(
                _get_send_prop_type_name(prop.type), prop.name))

            if prop.type != SendPropType.DATATABLE:
                continue

            if prop.name == 'baseclassx':
                continue

            for prop in prop.data_table:
                print('------------------{} : {}'.format(
                    _get_send_prop_type_name(prop.type), prop.name))

        current = current.next

def dumpstringtable(*args):
    """Outputs a specific string table item"""
    raise NotImplementedError

def effect(*args):
    """Performs a particular effect."""
    raise NotImplementedError

def emitsound(*args):
    """Plays a sound from an entity."""
    raise NotImplementedError

def enable(*args):
    """Enables a script that has been loaded."""
    raise NotImplementedError

def entcreate(*args):
    """Creates an entity where a player is looking."""
    raise NotImplementedError

def entitygetvalue(index, value_name):
    """Get a value name for a given entity."""
    return BaseEntity(index).get_key_value_string(value_name)

def entitysetvalue(index, value_name, value):
    """Set a value name for a given entity."""
    BaseEntity(index).set_key_value_string(value_name, value)

def entsetname(*args):
    """Names the entity the player is looking at. (DOES NOT SET PLAYER NAME)"""
    raise NotImplementedError

def escinputbox(*args):
    """Sends an ESC input box to a player."""
    raise NotImplementedError

def escmenu(*args):
    """Sends an ESC menu to a player."""
    raise NotImplementedError

def esctextbox(*args):
    """Sends an ESC textbox to a player."""
    raise NotImplementedError

def event(command, event_name, value_name=None, value=None):
    """Create and fire events to signal to plugins that an event has happened. It must be an event loaded via es_loadevents."""
    global _current_event
    if _current_event is not None and _current_event.name != event_name:
        dbgmsg(
            0,
            ('WARNING: A script is calling \'es_event {}\' for {} when the exis' +
             'ting event {} has not been cancelled or fired. Trying to continue' +
             ' anyway...').format(command, event_name, _current_event.name)
        )

    if command == 'initialize':
        _current_event = game_event_manager.create_event(event_name, True)
    elif command == 'cancel':
        if _current_event is not None:
            game_event_manager.free_event(_current_event)
            _current_event = None
    elif command == 'fire':
        if _current_event is not None:
            game_event_manager.fire_event(_current_event)
            _current_event = None
    elif value_name is not None and value is not None:
        if command == 'setint':
            _current_event.set_int(value_name, atoi(value))
        elif command == 'setfloat':
            _current_event.set_float(value_name, atof(value))
        elif command == 'setstring':
            _current_event.set_string(value_name, value)

def exists(identifier, value):
    """Checks whether a keygroup, keys, variable, or function exists."""
    if identifier == 'variable':
        return int(cvar.find_var(value) is not None)

    if identifier == 'map':
        return int(engine_server.is_map_valid(value))

    if identifier == 'saycommand':
        return int(value in SayCommandGenerator())

    if identifier == 'clientcommand':
        return int(value in ClientCommandGenerator())

    if identifier == 'command':
        command = cvar.find_command(value)
        return int(bool(command and command.is_command()))

    if identifier == 'keygroup':
        raise NotImplementedError

    if identifier == 'userid':
        try:
            edict_from_userid(atoi(value))
        except ValueError:
            return 0

        return 1

    if identifier == 'key':
        raise NotImplementedError

    if identifier == 'keyvalue':
        raise NotImplementedError

    if identifier == 'script':
        raise NotImplementedError

    if identifier == 'block':
        raise NotImplementedError

    return 0

def fadevolume(*args):
    """Fades the volume for a client."""
    raise NotImplementedError

def fire(*args):
    """Fires an entity trigger."""
    raise NotImplementedError

def flags(action, flag_name, convar_name):
    """Adds or removes the cheat flag from a command or variable. (EXPERIMENTAL/UNSUPPORTED)"""
    convar = cvar.find_command(convar_name)
    if convar is None:
        dbgmsg(0, 'Could not find var or command: {}'.format(convar_name))
        return

    if action == 'add':
        convar.add_flags(_get_convar_flag(flag_name))
    elif action == 'remove':
        convar.remove_flags(_get_convar_flag(flag_name))

def forcecallbacks(name):
    """Calls all global convar callbacks for a particular server variable."""
    convar = cvar.find_var(name)
    if convar:
        convar.call_global_change_callbacks(
            convar, convar.get_string(), convar.get_float())

def forcevalue(*args):
    """Forces a variable to a particular value"""
    raise NotImplementedError

def foreachkey(*args):
    """EXPERIMENTAL. Loops through a keygroup and performs a single command on each key, providing a single variable with the key name."""
    raise NotImplementedError

def foreachval(*args):
    """EXPERIMENTAL. Loops through a keygroup and performs a single command on each key, providing a single variable with the key name."""
    raise NotImplementedError

def formatqv(*args):
    """Allows you to format a string by filling in a list of strings into a format string."""
    raise NotImplementedError

def getCurrentEventVarFloat(name):
    """Returns the value of a named event variable in integer form."""
    return float(current_event_vars.get(name, 0))

def getCurrentEventVarInt(name):
    """Returns the value of a named event variable in integer form."""
    return int(current_event_vars.get(name, 0))

def getCurrentEventVarIsEmpty(name):
    """Returns 1 if the named event variable doesn't exist."""
    return int(name not in current_event_vars)

def getCurrentEventVarString(name):
    """Returns the value of a named event variable in string form."""
    return str(current_event_vars.get(name, ''))

def getEntityIndexes(classname=None):
    """Returns list of all entity indexes on the server, optionally filtered by a classname"""
    result = list()
    for entity in EntityIter(classname):
        result.append(entity.index)

    return result

def getEventInfo(name):
    """Gets the value of a particular event variable."""
    return str(current_event_vars.get(name, ''))

def getFlags(name):
    """Gets the flags value for a command"""
    return cvar.find_command(name).flags

def getFloat(name):
    """Gets the float value for a server variable"""
    convar = cvar.find_var(name)
    return convar and convar.get_float()

def getHelpText(name):
    """Gets the help text for a console command or server variable."""
    convar = cvar.find_command(name)
    return convar and convar.help_text

def getInt(name):
    """Gets the int value for a server variable"""
    convar = cvar.find_var(name)
    return convar and convar.get_int()

def getString(name):
    """Gets the string value for a server variable"""
    convar = cvar.find_var(name)
    return '' if convar is None else convar.get_string()

def getUseridList(*args):
    """Returns a list of the userids of all players on the server."""
    result = list()
    for player in PlayerIter():
        result.append(player.userid)

    return result

def getargc():
    """Gets the count of parameters passed to the current ES console command."""
    return command_info.argc

def getargs():
    """Gets the commandstring passed to the current ES console command."""
    return command_info.args

def getargv(index):
    """Gets the command parameter passed to the current ES console command."""
    return command_info.get_argv(index)

def getclientvar(userid, var_name):
    """Reads a console variable from a given player."""
    try:
        index = index_from_userid(atoi(userid))
    except ValueError:
        dbgmsg(0, 'userid not found: {}'.format(userid))
        return

    return engine_server.get_client_convar_value(var_name)

def getcmduserid():
    """Gets the commandstring passed to the current Valve console command."""
    return command_info.userid

def getentityindex(classname):
    """Gets the index for the first named entity found by that name. Returns -1 if not found."""
    entity = Entity.find(classname)
    return -1 if entity is None else entity.index

def getentitypropoffset(index, offset, prop_type):
    """Gets a server class property for a particular entity index"""
    pointer = pointer_from_index(index)
    if prop_type == SendPropType.INT:
        return pointer.get_int(offset)

    if prop_type == SendPropType.FLOAT:
        return pointer.get_float(offset)

    if prop_type == SendPropType.VECTOR:
        return ','.join(memory.make_object(Vector, pointer.get_pointer(offset)))

    return None

def getgame():
    """Returns the name of the Source game being played."""
    return server_game_dll.game_description

def getgravityvector(*args):
    """Returns the gravity vector."""
    raise NotImplementedError

def gethandlefromindex(index):
    """Gets the handle for an entity from its integer index."""
    try:
        return inthandle_from_index(index)
    except ValueError:
        return 0

def getindexfromhandle(inthandle):
    """Gets the index for an entity from its integer handle."""
    try:
        return index_from_inthandle(inthandle)
    except ValueError:
        return 0

def getindexprop(index, prop):
    """Gets a server class property for a particular entity index"""
    entity = BaseEntity(index)
    prop_type, offset = _get_prop_info(prop)
    if prop_type is None:
        return None

    ptr = entity.pointer
    if prop_type == SendPropType.INT:
        return ptr.get_int(offset)

    if prop_type == SendPropType.FLOAT:
        return ptr.get_float(offset)

    if prop_type == SendPropType.VECTOR:
        return ','.join(memory.make_object(Vector, ptr.get_pointer(offset)))

    if prop_type == SendPropType.STRING:
        return ptr.get_string(offset)

    return None

def getlivingplayercount(team=None):
    """Stores the count of living players on the server into a variable. Optionally a team can be specified. Returns -1 on error."""
    count = 0
    for player in PlayerIter():
        if _is_dead(player):
            continue

        if team is None:
            count += 1
        elif team == player.team:
            count += 1

    return count

def getmaxplayercount():
    """Stores the maximum number of player slots the server allows."""
    return global_vars.max_clients

def getplayercount(team):
    """Stores the count of players on the server into a variable. Optionally a team can be specified. Returns -1 on error."""
    count = 0
    for player in PlayerIter():
        if team is None:
            count += 1
        elif team == player.team:
            count += 1

    return count

def getplayerhandle(userid):
    """Gets the handle for a player class property using an entity handle (Untested)"""
    return Player.from_userid(atoi(userid)).inthandle

def getplayerlocation(userid):
    """Stores the player's current x, y, and z location (in 3 different variables or a 3-tuple in Python)."""
    return tuple(Player.from_userid(atoi(userid)).origin)

def getplayermovement(userid):
    """Stores the player's current forward movement value, side movement value, and upward movement value (in 3 different variables or Python 3-tuple)."""
    bcmd = Player.from_userid(atoi(userid)).last_user_command
    return (bcmd.forward_move, bcmd.side_move, bcmd.up_move)

def getplayername(userid):
    """Stores the player's name in the variable."""
    return Player.from_userid(atoi(userid)).name

def getplayerprop(userid, prop):
    """Gets a server class property for a particular player"""
    return getindexprop(index_from_userid(atoi(userid)), prop)

def getplayersteamid(userid):
    """Stores the player's STEAMID in the variable."""
    return Player.from_userid(atoi(userid)).steamid

def getplayerteam(userid):
    """Stores the player's team # in the variable."""
    return Player.from_userid(atoi(userid)).team

def getpropoffset(name):
    """Gets a server class property offset for a particular property path"""
    prop_type, offset = _get_prop_info(name)
    return 0 if offset is None else offset

def getproptype(name):
    """Gets a server class property type for a particular property path"""
    prop_type, offset = _get_prop_info(name)
    return 0 if prop_type is None else int(prop_type)

def getuserid(*args):
    """Looks-up a userid based on the string provided. Checks it against a userid, steamid, exact name, and partial name. (Based on Mani's algorithm.)"""
    raise NotImplementedError

def give(*args):
    """Gives the player a named item."""
    raise NotImplementedError

def isbot(*args):
    """Checks a userid to see if it's a bot, stores 1 in the variable if so, 0 if not."""
    return Player.from_userid(atoi(userid)).is_fake_client()

def isdedicated(*args):
    """Returns 1 in the variable if the server a dedicated server."""
    return engine_server.is_dedicated_server()

def keycreate(*args):
    """Creates a key that can be free-floating or associated with a group. Must call es_keydelete to free this memory when you're done."""
    raise NotImplementedError

def keydelete(*args):
    """Deletes a key from memory so that it's not leaked when you're done with it."""
    raise NotImplementedError

def keygetvalue(*args):
    """Gets a value within a given key (where the key could be free-floating or associated with a group)."""
    raise NotImplementedError

def keygroupcopy(*args):
    """Copies a keygroup."""
    raise NotImplementedError

def keygroupcreate(*args):
    """Creates a keygroup that can be loaded and saved to a file. Must call es_keygroupdelete to free this memory!"""
    raise NotImplementedError

def keygroupdelete(*args):
    """Deletes a keygroup from memory so that it's not leaked."""
    raise NotImplementedError

def keygroupfilter(*args):
    """Deletes keys from a keygroup that match or don't match a certain value."""
    raise NotImplementedError

def keygroupgetpointer(*args):
    """Returns the C++ pointer to a keygroup."""
    raise NotImplementedError

def keygroupload(*args):
    """Loads a keygroup from file based on its name."""
    raise NotImplementedError

def keygroupmsg(*args):
    """Sends a keygroup-based message to a player."""
    raise NotImplementedError

def keygrouprename(*args):
    """Renames an existing keygroup."""
    raise NotImplementedError

def keygroupsave(*args):
    """Saves a keygroup to a file based on its name."""
    raise NotImplementedError

def keylist(*args):
    """Lists all key values in memory that aren't groups. Optionally can look up a group, if you provide one."""
    raise NotImplementedError

def keypcreate(*args):
    """Returns the C++ pointer to a new keyvalues object."""
    raise NotImplementedError

def keypcreatesubkey(*args):
    """Creates a subkey as an integer."""
    raise NotImplementedError

def keypdelete(*args):
    """Deletes a key by pointer (not recommended)"""
    raise NotImplementedError

def keypdetachsubkey(*args):
    """Detaches a subkey by pointer."""
    raise NotImplementedError

def keypfindsubkey(*args):
    """Finds or creates a subkey by a particular name."""
    raise NotImplementedError

def keypgetdatatype(*args):
    """Returns the data type id of the value in the key."""
    raise NotImplementedError

def keypgetfirstsubkey(*args):
    """Retrieves the first subkey underneath this pointer"""
    raise NotImplementedError

def keypgetfirsttruesubkey(*args):
    """Retrieves the first true subkey for this pointer."""
    raise NotImplementedError

def keypgetfirstvaluekey(*args):
    """Retrieves the first value in this pointer."""
    raise NotImplementedError

def keypgetfloat(*args):
    """Retrieves the float value in this pointer by name."""
    raise NotImplementedError

def keypgetint(*args):
    """Retrieves the int value in this pointer by name."""
    raise NotImplementedError

def keypgetname(*args):
    """Gets a key name by pointer"""
    raise NotImplementedError

def keypgetnextkey(*args):
    """Retrieves the next key (peer) to this pointer."""
    raise NotImplementedError

def keypgetnexttruesubkey(*args):
    """Retrieves the next true subkey to this pointer (ignores 'values')"""
    raise NotImplementedError

def keypgetnextvaluekey(*args):
    """Retrieves the next value in this pointer."""
    raise NotImplementedError

def keypgetstring(*args):
    """Retrieves the string value in this pointer by name."""
    raise NotImplementedError

def keypisempty(*args):
    """Check if the keyvalue pointer is empty."""
    raise NotImplementedError

def keyploadfromfile(*args):
    """Saves the keyvalue pointer to filepath with all subkeys and values"""
    raise NotImplementedError

def keyprecursivekeycopy(*args):
    """Recursively copies a key into another key"""
    raise NotImplementedError

def keypsavetofile(*args):
    """Saves the keyvalue pointer to filepath with all subkeys and values"""
    raise NotImplementedError

def keypsetfloat(*args):
    """Sets the float value in this pointer by name."""
    raise NotImplementedError

def keypsetint(*args):
    """Sets the int value in this pointer by name."""
    raise NotImplementedError

def keypsetname(*args):
    """Sets a key name by pointer"""
    raise NotImplementedError

def keypsetstring(*args):
    """Sets the string value in this pointer by name."""
    raise NotImplementedError

def keyrename(*args):
    """Rename a key."""
    raise NotImplementedError

def keysetvalue(*args):
    """Sets a value within a given key (where the key could be free-floating or associated with a group)."""
    raise NotImplementedError

def lightstyle(style, value):
    """Set light style."""
    engine_server.light_style(int(style), value)

def load(addon=None):
    """Loads a script or lists all loaded scripts if no script is provided."""
    import es
    if addon is None:
        es.printScriptList()
    else:
        es.loadModuleAddon(addon)

def loadevents(*args):
    """Reads an event file and registers EventScripts as a handler for those events."""
    if len(args) == 1:
        game_event_manager.load_events_from_file(args[0])
    elif len(args) == 2:
        # Unnecessary to implement, because the event system is using a pre-hook
        pass

def log(msg):
    """Logs a message to the server log."""
    engine_server.log_print(msg)

def logv(name):
    """Logs the text inside of a variable."""
    convar = cvar.find_var(name)
    if convar:
        log(convar.get_string())

def makepublic(name):
    """Makes a console variable public such that changes to it are announced to clients."""
    convar = cvar.find_var(name)
    if convar:
        convar.make_public()

def mathparse(*args):
    """Adds a say command that refers to a particular block."""
    raise NotImplementedError

def menu(duration, userid, msg, options=''):
    """Sends an AMX-Style menu to the users"""
    try:
        index = index_from_userid(atoi(userid))
    except ValueError:
        return

    duration = atoi(duration)
    ShowMenu(
        msg,
        _get_menu_options(options),
        -1 if duration == 0 else duration
    ).send(index)

def msg(color, msg=None):
    """Broadcasts a message to all players. If the first word of the message is '#green', or '#lightgreen' then the message is displayed in that color, supports '#multi' also for embedded #green/#lightgreen in the message."""
    msg = _prepare_msg(color, msg)
    SayText2(msg).send()
    dbgmsg(0, msg)

def old_mexec(*args):
    """Runs an exec file from memory."""
    raise NotImplementedError

def physics(*args):
    """Interface with the Source physics engine (physics gravity, object velocity, etc)."""
    raise NotImplementedError

def playsound(*args):
    """Plays a sound to a player."""
    raise NotImplementedError

def precachedecal(modelpath):
    """Precache a decal and return its index."""
    engine_server.precache_decal(modelpath)

def precachemodel(modelpath):
    """Precache a model and return its index."""
    engine_server.precache_model(modelpath)

def precachesound(soundpath):
    """Precache sound."""
    engine_server.precache_sound(soundpath)

def printmsg(*args):
    """Outputs a message to the console."""
    raise NotImplementedError

def prop_dynamic_create(*args):
    """See prop_dynamic_create for syntax, but requires a userid first"""
    raise NotImplementedError

def prop_physics_create(*args):
    """See prop_physics_create for syntax, but requires a userid first."""
    raise NotImplementedError

def queryclientvar(userid, cvar_name):
    """Sends a request to query a client's console variable."""
    engine_server.start_query_cvar_value(
        edict_from_userid(atoi(userid)), cvar_name)

def queryregclientcmd(command):
    """Queries which block a particular client cmd is pointed to."""
    try:
        return client_command_proxies.get_proxy(command).block_name
    except KeyError:
        dbgmsg(0, 'Command {} wasn\'t registered.'.format(command))
        return ''

def queryregcmd(command):
    """Queries which block a console command refers to."""
    try:
        return server_command_proxies.get_proxy(command).block_name
    except KeyError:
        dbgmsg(0, 'Command {} wasn\'t registered.'.format(command))
        return ''

def queryregsaycmd(command):
    """Queries which block a particular say cmd is pointed to."""
    try:
        return say_command_proxies.get_proxy(command).block_name
    except KeyError:
        dbgmsg(0, 'Command {} wasn\'t registered.'.format(command))
        return ''

def refreshpublicvars():
    """Outputs all the console commands and variables."""
    current = cvar.commands
    while current:
        if not current.is_command() and current.is_flag_set(ConVarFlags.NOTIFY):
            cvar.call_global_change_callbacks(
                current, current.get_string(), current.get_float())

        current = current.next

def regclientcmd(command, block_name, description):
    """Adds a client command that refers to a particular block."""
    if command in client_command_proxies:
        dbgmsg(0, 'Command {} already exists.'.format(command))
        return

    get_client_command(command).add_callback(
        client_command_proxies.create_proxy(command, block_name))

def regcmd(command, block_name, description):
    """Adds a console command that refers to a particular block."""
    if cvar.find_command(command) is not None:
        dbgmsg(0, 'Command {} already exists.'.format(command))
        return

    get_server_command(command, description).add_callback(
        server_command_proxies.create_proxy(command, block_name))

def regex(*args):
    """Various regular expression commands."""
    raise NotImplementedError

def regsaycmd(command, block_name, description):
    """Adds a say command that refers to a particular block."""
    if command in say_command_proxies:
        dbgmsg(0, 'Command {} already exists.'.format(command))
        return

    get_say_command(command).add_callback(
        say_command_proxies.create_proxy(command, block_name))

def reload(addon):
    """Reloads a script that is loaded."""
    import es
    es.unloadModuleAddon(addon)
    es.loadModuleAddon(addon)

def remove(*args):
    """Removes an entity class"""
    raise NotImplementedError

def scriptpacklist(*args):
    """Lists the script packs running on the server. If a userid is provided, will es_tell the list to the user."""
    raise NotImplementedError

def sendkeypmsg(*args):
    """Sends a client message based on a KeyValues pointer. sendkeypmsg(userid,type,keyid)"""
    raise NotImplementedError

def set(name, value, description):
    """Adds/sets a new server/global variable."""
    ConVar(name, str(value), description)

def setFloat(name, value):
    """Sets the server variable to the given float value. Creating it if necessary."""
    convar = ConVar(name, str(value))
    return convar.get_float()

def setInt(name, value):
    """Sets the server variable to the given integer value. Creating it if necessary."""
    convar = ConVar(name, str(value))
    return convar.get_int()

def setNumRegistered(*args):
    """Internal command for setting number of ticklisteners registered."""
    # No need to implement

def setString(name, value):
    """Sets the server variable to the given string  value. Creating it if necessary."""
    convar = ConVar(name, str(value))
    return convar.get_string()

def setang(userid, pitch, yaw, roll=0):
    """Sets player view angle."""
    Player.from_userid(atoi(userid)).teleport(
        None, QAngle(atof(pitch), atof(yaw), atof(roll)), None)

def setentityname(index, targetname):
    """Sets the targetname of an entity by index."""
    BaseEntity(index).set_key_value_string('targetname', targetname)

def setentitypropoffset(index, offset, type, value):
    """Gets a server class property for a particular entity index"""
    pointer = pointer_from_index(atoi(index))
    if prop_type == SendPropType.INT:
        return pointer.set_int(int(value), offset)

    if prop_type == SendPropType.FLOAT:
        return pointer.set_float(float(value), offset)

    if prop_type == SendPropType.VECTOR:
        x, y, z = splitvectorstring(value)
        ptr.set_float(x, offset + 0)
        ptr.set_float(y, offset + 4)
        ptr.set_float(z, offset + 8)

def setindexprop(index, prop, value):
    """Sets a server class property for the given entity index"""
    entity = BaseEntity(atoi(index))
    prop_type, offset = _get_prop_info(prop)
    if prop_type is None:
        return None

    ptr = entity.pointer
    if prop_type == SendPropType.INT:
        return ptr.set_int(int(value), offset)

    if prop_type == SendPropType.FLOAT:
        return ptr.set_float(int(value), offset)

    if prop_type == SendPropType.VECTOR:
        x, y, z = splitvectorstring(value)
        ptr.set_float(x, offset + 0)
        ptr.set_float(y, offset + 4)
        ptr.set_float(z, offset + 8)

def setinfo(variable, value):
    """Adds a new server/global variable."""
    ConVar(variable, value)

def setplayerprop(userid, prop, value):
    """Sets a server class property for the given player"""
    setindexprop(index_from_userid(atoi(userid)), prop, value)

def setpos(userid, x, y, z):
    """Teleports a player."""
    Player.from_userid(atoi(userid)).teleport(
        Vector(atof(x), atof(y), atof(z)), None, None)

def setview(userid, entity_index=None):
    """Changes a players view to share that of a particular entity index."""
    player_edict = edict_from_userid(atoi(userid))
    if entity_index is None:
        view_edict = player_edict
    else:
        view_edict = edict_from_index(entity_index)

    engine_server.set_view(player_edict, view_edict)

def sexec(userid, commandstring):
    """Forces a userid to execute a command on the server console (bypassing client console)."""
    Player.from_userid(atoi(userid)).client_command(commandstring, True)

def sexec_all(commandstring):
    """Forces all users to execute a command on the server console."""
    for player in PlayerIter():
        player.client_command(commandstring, True)

def showMenu(*args):
    """Sends an AMX-Style menu to the users"""
    menu(*args)

def soon(commandstring):
    """Adds a command to the end of the command queue."""
    engine_server.server_command(commandstring)

def spawnentity(entity_index):
    """Spawn a given entity index."""
    BaseEntity(entity_index).spawn()

def spawnplayer(userid):
    """Spawn a player with the given userid."""
    Player.from_userid(atoi(userid)).spawn()

def splitvectorstring(vectorstring):
    """Stores the vector's current x, y, and z as read from the vector in string form."""
    return tuple(map(float, vectorstring.split(',')))

def sql(*args):
    """Local database support"""
    raise NotImplementedError

def stopsound(*args):
    """Stops a specific sound for a player."""
    raise NotImplementedError

def stringtable(*args):
    """Update an entry in a stringtable"""
    raise NotImplementedError

def tell(userid, color, msg=None):
    """Sends HUD message to one player. If the first word of the message is '#green', or '#lightgreen' then the message is displayed in that color. Supports '#multi' also for embedded #green/#lightgreen in the message."""
    SayText2(_prepare_msg(color, msg)).send(index_from_userid(atoi(userid)))

def toptext(*args):
    """Sends HUD message to one player."""
    raise NotImplementedError

def trick(*args):
    """Miscellaneous tricky things."""
    raise NotImplementedError

def unload(addon):
    """Unloads a script that has been loaded."""
    import es
    es.unloadModuleAddon(addon)

def unregclientcmd(command):
    """Removes a client command that refers to a particular block."""
    try:
        proxy = client_command_proxies.pop(command)
    except KeyError:
        dbgmsg(0, 'unregclientcmd: Did not find command: {}'.format(command))
    else:
        get_client_command(command).remove_callback(proxy)

def unregsaycmd(command):
    """Removes a say command that refers to a particular block."""
    try:
        proxy = say_command_proxies.pop(command)
    except KeyError:
        dbgmsg(0, 'unregsaycmd: Did not find command: {}'.format(command))
    else:
        get_say_command(command).remove_callback(proxy)

def usermsg(*args):
    """Create and send a usermsg to a client."""
    raise NotImplementedError

def voicechat(command, to_userid, from_userid):
    """Allows you to control listening players."""
    try:
        to_index = index_from_userid(atoi(to_userid))
    except ValueError:
        # TODO: ErrorMsg
        return

    try:
        from_index = index_from_userid(atoi(from_userid))
    except ValueError:
        # TODO: ErrorMsg
        return

    command = command.lower()
    if command == 'islistening':
        return int(voice_server.get_client_listening(to_index, from_index))
    elif command == 'listen' or command == 'nolisten':
        voice_server.set_client_listening(
            to_index, from_index, command == 'listen')