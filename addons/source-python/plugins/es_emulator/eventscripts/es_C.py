# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import muparser

# Source.Python
#   Memory
import memory
#   Cvars
from cvars import cvar
from cvars.flags import ConVarFlags
#   Commands
from commands import Command
from commands.say import SayCommandGenerator
from commands.say import get_say_command
from commands.client import ClientCommandGenerator
from commands.client import get_client_command
from commands.server import get_server_command
#   Effects
from effects.base import TempEntity
#   Engines
from engines.server import engine_server
from engines.server import global_vars
from engines.server import server_game_dll
from engines.server import queue_command_string
from engines.sound import engine_sound
from engines.sound import Pitch
#   Events
from events.manager import game_event_manager
#   Messages
from messages import UserMessage
from messages import TextMsg
from messages import SayText2
from messages import ShowMenu
from messages import DialogType
from messages.dialog import create_message
#   Players
from players import PlayerGenerator
from players.entity import Player
from players.helpers import index_from_userid
from players.helpers import userid_from_edict
from players.helpers import edict_from_userid
from players.helpers import userid_from_inthandle
from players.voice import voice_server
#   Entities
from entities import EntityGenerator
from entities.entity import BaseEntity
from entities.entity import Entity
from entities.helpers import index_from_edict
from entities.helpers import inthandle_from_index
from entities.helpers import index_from_inthandle
from entities.helpers import edict_from_index
from entities.helpers import pointer_from_index
from entities.props import SendPropType
#   Filters
from filters.players import PlayerIter
from filters.entities import EntityIter
from filters.recipients import RecipientFilter
#   Listeners
from listeners.tick import Delay
#   Mathlib
from mathlib import QAngle
from mathlib import Vector
#   Net Channel
from net_channel import NetFlow
#   Steam
from steam import SteamID
#   Stringtables
from stringtables import string_tables
from stringtables import INVALID_STRING_INDEX
#   KeyValues
from keyvalues import KeyValues
#   Physics
from physics import physics
#   Plugins
from plugins.manager import plugin_manager

# ES Emulator
#   Logic
from es_emulator.logic import current_event_vars
from es_emulator.logic import server_command_proxies
from es_emulator.logic import say_command_proxies
from es_emulator.logic import client_command_proxies
from es_emulator.logic import command_info
from es_emulator.logic import register_for_event_file
#   Helpers
from es_emulator.helpers import *
#   Cvars
from es_emulator.cvars import datadir_cvar
from es_emulator.cvars import scriptdir_cvar
from es_emulator.cvars import debug_cvar
from es_emulator.cvars import debuglog_cvar


# =============================================================================
# >> __all__
# =============================================================================
# TODO:
#__all__ = ()


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# Helper variable for es.event()
_current_event = None

# Helpers for KeyValues stuff
user_keys = KeyValues('UserKeys')

user_groups = KeyValues('UserGroups')
user_keys.add_sub_key(user_groups)

ungrouped = KeyValues('Ungrouped')
user_keys.add_sub_key(ungrouped)

def _find_group(argv):
    if len(argv) == 3:
        name = argv[1]
        group = user_groups.find_key(name)
        if group is None:
            dbgmsg(0, 'ERROR: Eventscripts cannot find the {} group!'.format(name))
            _set_last_error('Keygroup not found')

        return group, argv[2]

    return ungrouped, argv[1]

def _get_full_path(argv):
    if len(argv) == 3:
        if argv[2][0] == '|':
            full_path = KEYGROUP_LOAD_FORMAT.format(
                'addons/source-python/plugins/es_emulator/eventscripts',
                argv[2][1:], argv[1])
        else:
            full_path = KEYGROUP_LOAD_FORMAT.format(
                datadir_cvar.get_string(), argv[2], argv[1])
    else:
        full_path = KEYGROUP_LOAD_FORMAT.format(
            datadir_cvar.get_string(), scriptdir_cvar.get_string(), argv[1])

    return full_path

_key_values = {}

def _make_keyvalues(key_ptr):
    return memory.make_object(KeyValues, memory.Pointer(key_ptr))

def _get_keyvalues_ptr(key):
    return memory.get_object_pointer(key).address

def _store_key_value(kv):
    addr = memory.get_object_pointer(kv).address
    _key_values[addr] = kv
    return addr

def _remove_key_value(addr):
    _key_values.pop(addr, 0)

def dict_to_keyvalues(name, data):
    result = user_groups.find_key(name, True)
    for key, value in data.items():
        _dict_to_keyvalues(result, key, value)

    return result

def _dict_to_keyvalues(result, key, value):
    if isinstance(value, dict):
        r = result.find_key(str(key), True)
        for k, v in value.items():
            _dict_to_keyvalues(r, k, v)
    elif isinstance(value, str):
        result.set_string(key, value)
    elif isinstance(value, int):
        result.set_int(key, value)
    elif isinstance(value, float):
        result.set_float(key, value)
    else:
        raise NotImplementedError


# =============================================================================
# >> CONSTANTS
# =============================================================================
KEYGROUP_LOAD_FORMAT = '{}/{}/es_{}_db.txt'


# =============================================================================
# >> ES FUNCTIONS
# =============================================================================
# Pure Python function
def ForceServerCommand(command_str):
    """Inserts a command to the server queue at the beginning and forces execution."""
    if not isinstance(command_str, str):
        raise TypeError

    c = Command()
    if not c.tokenize(command_str):
        return 1

    con_command = cvar.find_command(c[0])
    if con_command:
        con_command.dispatch(c)
    else:
        convar = cvar.find_var(c[0])
        if convar:
            convar.set_string(c.arg_string)
        else:
            queue_command_string(command_str)
            #engine_server.insert_server_command()

    return 1

# Pure Python function
def InsertServerCommand(command_str):
    """Inserts a command to the server queue at the beginning."""
    if not isinstance(command_str, str):
        raise TypeError

    queue_command_string(command_str)
    #engine_server.insert_server_command(command_str)
    return 1

# Pure Python function
def ServerCommand(command_str):
    """Adds a command to the end of the server queue."""
    if not isinstance(command_str, str):
        raise TypeError

    queue_command_string('wait;{}'.format(command_str))
    return 1

def _disable(*args):
    """EventScripts internal command."""
    # No need to implement

def _foreachkey(*args):
    """EXPERIMENTAL. Loops through a keygroup and performs a single command on each key, providing a single variable with the key name."""
    # No need to implement

def _foreachval(*args):
    """EXPERIMENTAL. Loops through a keygroup and performs a single command on each key, providing a single variable with the key name."""
    # No need to implement

def _unload(*args):
    """EventScripts internal command."""
    # No need to implement

@command
def botsetvalue(argv):
    """Sets a convar value for a fake client."""
    userid = argv[1]
    try:
        edict = edict_from_userid(atoi(userid))
    except ValueError:
        dbgmsg(0, 'SetFakeClientConvarValue: Unable to find player')
        _set_last_error('Invalid userid')
    else:
        convar_name = argv[2]
        value = argv[3]
        engine_server.set_fake_client_convar_value(edict, convar_name, value)
        dbgmsg(1, 'Set client var: {}, {} = {}'.format(
            userid, convar_name, value))

@command
def centermsg(argv):
    """Broadcasts a centered HUD message to all players."""
    TextMsg(argv.arg_string).send()

@command
def centertell(argv):
    """Sends a centered HUD message to all players."""
    str_userid = argv[1]
    userid = atoi(str_userid)
    msg = argv.arg_string[len(str_userid)+1:]
    if userid > 0:
        try:
            index = index_from_userid(userid)
        except ValueError:
            return

        TextMsg(msg).send(index)
    else:
        centermsg(msg)

@command
def cexec(argv):
    """Forces a userid to execute a command in their console."""
    userid = argv[1]
    try:
        player = Player.from_userid(atoi(userid))
    except ValueError:
        return

    _cexec(player, argv.arg_string[len(userid)+1])

@command
def cexec_all(argv):
    """Forces all users to execute a command in their console."""
    for player in PlayerIter():
        _cexec(player, argv.arg_string)

@command
def changeteam(argv):
    """Changes the team of the player."""
    userid = atoi(argv[1])
    try:
        player = Player.from_userid(userid)
    except ValueError:
        dbgmsg(0, 'Player doesn\'t exist: {}'.format(userid))
        return

    player.team = atoi(argv[2])

# Pure Python function
def cmdargc(*args):
    """Gets the command parameter count passed to the current Valve console command."""
    return command_info.argc

# Pure Python function
def cmdargs(*args):
    """Gets the commandstring passed to the current Valve console command."""
    return command_info.args

# Pure Python function
def cmdargv(index):
    """Gets the command parameter passed to the current Valve console command."""
    if not isinstance(index, int):
        raise TypeError

    return command_info.get_argv(index)

@command
def commandv(argv):
    """Just runs a command-string inside of the variable."""
    name = argv[1]
    convar = cvar.find_var(name)
    if convar:
        queue_command_string(convar.get_string())
        #engine_server.insert_server_command(convar.get_string())
    else:
        dbgmsg(0,'ERROR: variable {} does not exist.'.format(name))
        _set_last_error('Variable does not exist')

@command
def copy(argv):
    """Reads the server variable referenced by varname2 and copies it into the variable referenced by varname."""
    if len(argv) != 3:
        dbgmsg(0, 'Syntax: es_xcopy <varname> <varname2>')
        _set_last_error('Not enough arguments.')
        return

    var1_name = argv[1]
    var2_name = argv[2]
    if var1_name == '' or var2_name == '':
        dbgmsg(0, 'Specify a variable!')
        _set_last_error('Not enough arguments.')
        return


    var2 = cvar.find_var(var2_name)
    if var2 is None:
        dbgmsg(0, 'The var "{}" could not be found'.format(var2_name))
        return

    var1 = cvar.find_var(var1_name)
    if var1 is None:
        dbgmsg(0, 'The var "{}" could not be set.'.format(var1_name))
        return

    var1.set_string(var2.get_string())
    dbgmsg(1, '{} = \"{}"'.format(var1.name, var1.get_string()))

@command
def createbot(argv):
    """Adds a bot to the server."""
    try:
        return userid_from_edict(engine_server.create_fake_client(argv[1]))
    except ValueError:
        return None

@command
def createentity(argv):
    """Creates an entity somewhere by name."""
    entity = BaseEntity.create(argv[1])
    if len(argv) > 2:
        entity.set_key_value_string('targetname', argv[2])

    return entity.index

@command
def createentityindexlist(argv):
    """Creates a keygroup (or dictionary) of all indexes for an entity class or for all entities."""
    result = {}

    arg1 = argv[1]
    if arg1:
        generator = EntityGenerator(arg1)
    else:
        generator = EntityGenerator()

    for edict in generator:
        result[index_from_edict(edict)] = edict.classname

    return result

@command
def createentitylist(argv):
    """Creates a keygroup (or dictionary) for an entity class or for all entities."""
    result = {}
    for entity in EntityIter(argv[1] or None):
        temp = result[entity.index] = {}
        temp['classname'] = entity.classname
        temp['handle'] = entity.inthandle
        # TODO: Add a full server class dump

    return result

@command
def createplayerlist(argv):
    """Creates a new keygroup containing the current list of players."""
    if len(argv) == 1:
        players = PlayerIter()
    else:
        players = [Player.from_userid(atoi(argv[1]))]

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
            latency = info.get_avg_latency(NetFlow.OUTGOING)
            cmdrate = max(1, atoi(engine_server.get_client_convar_value(
                player.index, 'cl_cmdrate')))

            latency -= (0.5 / cmdrate) + global_vars.interval_per_tick * 0.5

            temp['ping'] = _clamp(int(latency * 1000), 5, 1000)
            temp['packetloss'] = _clamp(
                int(100 * info.get_avg_loss(NetFlow.INCOMING)), 0, 100)
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

@command
def createscriptlist(argv):
    """Creates a new keygroup containing the current list of players."""
    if len(argv) <= 1:
        return None

    # Fix cyclic import
    from esc import addons

    result = {}
    for name in addons:
        if len(argv) > 1 and name.lower() != argv[2].lower():
            continue

        result[name] = dict(
            status='{}abled'.format('dis' if addons[name].disabled else 'en'),
            type='txt')

    return result

@command
def createvectorfrompoints(argv):
    """Creates a vector-string that goes from point/vector A to point/vector B."""
    vec1 = splitvectorstring(argv[1])
    vec2 = splitvectorstring(argv[2])
    return createvectorstring(
        vec2[0] - vec1[0],
        vec2[1] - vec1[1],
        vec2[2] - vec1[2]
    )

@command
def createvectorstring(argv):
    """Creates a string form of three x y z variables representing a vector."""
    return '{},{},{}'.format(atof(argv[1]), atof(argv[2]), atof(argv[3]))

def _chunk_msg(msg, size):
    return (msg[0+i:size+i] for i in range(0, len(msg), size))

# Not quite pure Python (console command gets registred differently)
def dbgmsg(level, msg):
    """Outputs a message to the console."""
    level = int(level)

    if debug_cvar.get_int() < level:
        return 1

    if debuglog_cvar.get_int() == 1:
        output_func = engine_server.log_print
    else:
        output_func = Msg

    msg = str(msg)
    for chunk in _chunk_msg(msg, 1000):
        output_func(chunk + '\n')

    return 1

@command
def dbgmsgv(argv):
    """Prints a debug message for EventScripts"""
    convar_name = argv[2]
    convar = cvar.find_var(convar_name)
    if convar is not None:
        dbgmsg(atoi(argv[1]), convar.get_string())
    else:
        dbgmsg(0, 'ERROR: variable {} does not exist.'.format(convar_name))

@command
def delayed(argv):
    """Will run <commandstring>, after <seconds> seconds."""
    if len(argv) != 3:
        command_string = argv.arg_string[len(argv[1]):]
    else:
        command_string = argv[2]

    Delay(atof(argv[1]), queue_command_string, command_string)

def disable(*args):
    """Disables a script that has been loaded."""
    # No need to implement

@command
def doblock(argv):
    """Executes a block."""
    import es
    es.addons.callBlock(argv.arg_string)

def dosql(*args):
    """Does some SQL."""
    raise NotImplementedError

@command
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

@command
def dumpentities(argv):
    """Dumps to console all server classes and properties for all entities."""
    for entity in EntityIter():
        server_class = entity.server_class
        _dump_entity_table(
            entity,
            server_class.table,
            '{}[{}]: {}'.format(
                entity.index, entity.classname, server_class.name)
        )

@command
def dumpserverclasses(argv):
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

@command
def dumpstringtable(argv):
    """Outputs a specific string table item"""
    string_table = string_tables[argv[1]]
    if string_table is None:
        return

    index = string_table[argv[2]]
    if index != INVALID_STRING_INDEX:
        dbgmsg(0, 'Data:\n{}'.format(string_table[index]))
        dbgmsg(0, 'Data:\n{}'.format(string_table.get_user_data(index)))

@command
def effect(argv):
    """Performs a particular effect."""
    operation = argv[1].lower()
    if operation == 'sparks':
        entity = TempEntity('Sparks')
        entity.magnitude = atoi(argv[3])
        entity.trail_length = atoi(argv[4])
        entity.direction = Vector(*splitvectorstring(argv[5])) if len(argv) > 4 else None
        entity.origin = Vector(*splitvectorstring(argv[2]))
    elif operation == 'smoke':
        entity = TempEntity('Smoke')
        entity.scale = atof(argv[4]) * 0.1 # This is done in CEffectsServer
        entity.frame_rate = atoi(argv[5])
        entity.model_index = atoi(argv[3])
        entity.origin = Vector(*splitvectorstring(argv[2]))
    elif operation == 'beam':
        if len(argv) <= 17:
            dbgmsg(1, 'Incorrect syntax for es_effect beam.')
            return

        entity = TempEntity('BeamPoints')
        entity.alpha = atoi(argv[16])
        entity.blue = atoi(argv[15])
        entity.green = atoi(argv[14])
        entity.red = atoi(argv[13])
        entity.amplitude = atoi(argv[12])
        entity.end_width = atoi(argv[10])
        entity.life_time = atoi(argv[8])
        entity.start_width = atoi(argv[9])
        entity.fade_length = atoi(argv[11])
        entity.frame_rate = atoi(argv[7])
        entity.halo_index = atoi(argv[5])
        entity.model_index = atoi(argv[4])
        entity.speed = atoi(argv[17])
        entity.start_frame = atoi(argv[6])
        entity.end_point = Vector(*splitvectorstring(argv[3]))
        entity.start_point = Vector(*splitvectorstring(argv[2]))
    elif operation == 'dust':
        entity = TempEntity('Dust')
        entity.size = atof(argv[4])
        entity.speed = atof(argv[5])
        entity.direction = Vector(*splitvectorstring(argv[3]))
        entity.origin = Vector(*splitvectorstring(argv[2]))
    elif operation == 'energysplash':
        entity = TempEntity('Energy Splash')
        entity.explosive = bool(atoi(argv[4]))
        entity.direction = Vector(*splitvectorstring(argv[3]))
        entity.position = Vector(*splitvectorstring(argv[2]))
    else:
        return

    entity.create(RecipientFilter())

@command
def emitsound(argv):
    """Plays a sound from an entity."""
    sound = argv[3]
    engine_sound.precache_sound(sound)

    index = 0
    emitter_type = argv[1]
    emitter = atoi(argv[2])
    if emitter_type == 'player':
        try:
            index = index_from_userid(emitter)
        except ValueError:
            pass
    elif emitter_type == 'entity':
        index = emitter

    if not index:
        return

    flags = 0
    if len(argv) > 6:
        flags = atoi(argv[6])

    pitch = Pitch.NORMAL
    if len(argv) > 7:
        pitch = atoi(argv[7])

    engine_sound.emit_sound(RecipientFilter(), index, 0, sound, atof(argv[4]),
        atof(argv[5]), flags, pitch)

def enable(*args):
    """Enables a script that has been loaded."""
    # No need to implement

@command
def entcreate(argv):
    """Creates an entity where a player is looking."""
    try:
        player = Player.from_userid(atoi(argv[1]))
    except ValueError:
        return

    entity = argv[2]
    if not entity:
        return

    with _last_give_enabled():
        _exec_client_cheat_command(player, 'ent_create {} {}'.format(
            entity, ' '.join(argv.args[2:])))

@command
def entitygetvalue(argv):
    """Get a value name for a given entity."""
    try:
        return BaseEntity(atoi(argv[1])).get_key_value_string(argv[2])
    except ValueError:
        return ''

@command
def entitysetvalue(argv):
    """Set a value name for a given entity."""
    index = atoi(argv[1])
    try:
        BaseEntity(index).set_key_value_string(argv[2], argv[3])
    except ValueError:
        dbgmsg(0, 'Entity not found: {}'.format(index))

@command
def entsetname(argv):
    """Names the entity the player is looking at. (DOES NOT SET PLAYER NAME)"""
    try:
        player = Player.from_userid(atoi(argv[1]))
    except ValueError:
        return

    _exec_client_cheat_command(player, 'ent_setname {}'.format(argv[2]))

@command
def escinputbox(argv):
    """Sends an ESC input box to a player."""
    duration = atoi(argv[1])
    if not (10 <= duration <= 200):
        dbgmsg(0, 'Error: "{}" is an invalid specifier for <time>.'.format(argv[1]))
        dbgmsg(0, 'Error: <time> must be at least 10 or at the most 200.')
        return

    try:
        edict = edict_from_userid(atoi(argv[2]))
    except ValueError:
        dbgmsg(0, 'Error: "{}" is an invalid userid.'.format(argv[2]))
        return

    data = KeyValues('entryBox')
    data.set_string('title', argv[3])
    data.set_int('level', 0)
    data.set_color('color', Color(255, 255, 255, 255))
    data.set_int('time', duration)
    data.set_string('msg', argv[4].replace('\\n', '\n'))
    data.set_string('command', '"{}"'.format(argv[5]))
    create_message(edict, DialogType.ENTRY, data)

@command
def escmenu(argv):
    """Sends an ESC menu to a player."""
    duration = atoi(argv[1])
    if not (10 <= duration <= 200):
        dbgmsg(0, 'Error: "{}" is an invalid specifier for <time>.'.format(argv[1]))
        dbgmsg(0, 'Error: <time> must be at least 10 or at the most 200.')
        return

    try:
        edict = edict_from_userid(atoi(argv[2]))
    except ValueError:
        dbgmsg(0, 'Error: "{}" is an invalid userid.'.format(argv[2]))
        return

    data = KeyValues('menu')
    data.set_string('title', argv[3])
    data.set_int('level', 0)
    data.set_color('color', Color(255, 255, 255, 255))
    data.set_int('time', duration)
    data.set_string('msg', argv[4].replace('\\n', '\n'))

    for x in range(1, 9):
        argi = 4 + x
        if argi > len(argv) - 1:
            break

        button = data.find_key(str(x), True)
        button.set_string('msg', argv[argi])
        button.set_string('command', 'menuselect {};'.format(x))

    create_message(edict, DialogType.MENU, data)

@command
def esctextbox(argv):
    """Sends an ESC textbox to a player."""
    duration = atoi(argv[1])
    if not (10 <= duration <= 200):
        dbgmsg(0, 'Error: "{}" is an invalid specifier for <time>.'.format(argv[1]))
        dbgmsg(0, 'Error: <time> must be at least 10 or at the most 200.')
        return

    try:
        edict = edict_from_userid(atoi(argv[2]))
    except ValueError:
        dbgmsg(0, 'Error: "{}" is an invalid userid.'.format(argv[2]))
        return

    data = KeyValues('textBox')
    data.set_string('title', argv[3])
    data.set_int('level', 0)
    data.set_color('color', Color(255, 255, 255, 255))
    data.set_int('time', duration)
    data.set_string('msg', argv[4].replace('\\n', '\n'))
    create_message(edict, DialogType.TEXT, data)

@command
def event(argv):
    """Create and fire events to signal to plugins that an event has happened. It must be an event loaded via es_loadevents."""
    global _current_event
    operation = argv[1]
    event_name = argv[2]
    value_name = argv[3] if len(argv) > 3 else None
    value = argv[4] if len(argv) > 4 else None
    if _current_event is not None and _current_event.name != event_name:
        dbgmsg(
            0,
            ('WARNING: A script is calling \'es_event {}\' for {} when the ' +
             'existing event {} has not been cancelled or fired. Trying to ' +
             'continue anyway...').format(
                operation, event_name, _current_event.name)
        )

    if operation == 'initialize':
        _current_event = game_event_manager.create_event(event_name, True)
    elif operation == 'cancel':
        if _current_event is not None:
            game_event_manager.free_event(_current_event)
            _current_event = None
    elif operation == 'fire':
        if _current_event is not None:
            game_event_manager.fire_event(_current_event)
            _current_event = None
    elif value_name is not None and value is not None:
        if operation == 'setint':
            _current_event.set_int(value_name, atoi(value))
        elif operation == 'setfloat':
            _current_event.set_float(value_name, atof(value))
        elif operation == 'setstring':
            _current_event.set_string(value_name, value)

@command
def exists(argv):
    """Checks whether a keygroup, keys, variable, or function exists."""
    identifier = argv[1].lower()
    name = argv[2]
    name2 = argv[3] if len(argv) > 3 else None
    name3 = argv[4] if len(argv) > 4 else None
    if identifier == 'variable':
        return int(cvar.find_var(name) is not None)

    if identifier == 'map':
        return int(engine_server.is_map_valid(name))

    if identifier == 'saycommand':
        return int(name in SayCommandGenerator())

    if identifier == 'clientcommand':
        return int(name in ClientCommandGenerator())

    if identifier == 'command':
        return int(cvar.find_command(name) is not None)

    if identifier == 'keygroup':
        return int(user_groups.find_key(name) is not None)

    if identifier == 'userid':
        try:
            edict_from_userid(atoi(name))
        except ValueError:
            return 0

        return 1

    if identifier == 'key':
        if name2 is not None:
            group = user_groups.find_key(name)
            if group is None:
                return 0

            key_name = name2
        else:
            group = ungrouped
            key_name = name

        return int(group.find_key(key_name) is not None)

    if identifier == 'keyvalue':
        if len(argv) > 4:
            group = user_groups.find_key(name)
            if group is None:
                return 0

            key_name = name2
        else:
            group = ungrouped
            key_name = name

        new_key = group.find_key(key_name)
        if new_key is None:
            return 0

        if len(argv) > 4:
            value = new_key.find_key(name3)
        else:
            value = new_key.find_key(name2)

        return int(value is not None)

    # "script" and "block" gets monkeypatched by esc
    return 0

@command
def fadevolume(argv):
    """Fades the volume for a client."""
    try:
        edict = edict_from_userid(atoi(argv[1]))
    except ValueError:
        dbgmsg(0, 'FadeClientVolume: Unable to find player')
        return

    engine_server.fade_client_volume(
        edict, atof(argv[2]), atof(argv[3]), atof(argv[4]), atof(argv[5]))

@command
def fire(argv):
    """Fires an entity trigger."""
    userid = argv[1]
    try:
        player = Player.from_userid(atoi(userid))
    except ValueError:
        return

    _exec_client_cheat_command(
        player, 'ent_fire {}'.format(argv.arg_string[len(userid)+1:]))

@command
def flags(argv):
    """Adds or removes the cheat flag from a command or variable. (EXPERIMENTAL/UNSUPPORTED)"""
    convar_name = argv[3]
    convar = cvar.find_base(convar_name)
    if convar is None:
        dbgmsg(0, 'Could not find var or command: {}'.format(convar_name))
        return

    if not _can_change(convar):
        return

    action = argv[1].lower()
    flag_name = argv[2].lower()
    if action == 'add':
        convar.add_flags(_get_convar_flag(flag_name))
    elif action == 'remove':
        convar.remove_flags(_get_convar_flag(flag_name))

@command
def forcecallbacks(argv):
    """Calls all global convar callbacks for a particular server variable."""
    convar = cvar.find_var(argv[1])
    if convar:
        cvar.call_global_change_callbacks(
            convar, convar.get_string(), convar.get_float())

def forcevalue(*args):
    """Forces a variable to a particular value"""
    raise NotImplementedError

@command
def foreachkey(argv):
    """EXPERIMENTAL. Loops through a keygroup and performs a single command on each key, providing a single variable with the key name."""
    # Use the esc implementation
    ForceServerCommand('foreachkey {}'.format(argv.arg_string))

@command
def foreachval(argv):
    """EXPERIMENTAL. Loops through a keygroup and performs a single command on each key, providing a single variable with the key name."""
    # Use the esc implementation
    ForceServerCommand('foreachval {}'.format(argv.arg_string))

@command
def formatqv(argv):
    """Allows you to format a string by filling in a list of strings into a format string."""
    formatted = argv[1]
    for x in range(1, len(argv) - 1):
        convar_name = argv[x+1]
        convar = cvar.find_var(convar_name)
        if convar is None:
            dbgmsg(0, 'ERROR: variable {} does not exist.'.format(convar_name))
            _set_last_error('Variable does not exist')
            return None

        temp = formatted.replace('%{}'.format(x), convar.get_sttring())
        if temp == formatted:
            dbgmsg(0, 'ERROR: You did not provide enough parameters for the string you specified.')
            _set_last_error('Not enough arguments.')

    return formatted

# Pure Python function
def getCurrentEventVarFloat(name):
    """Returns the value of a named event variable in integer form."""
    if not isinstance(name, str):
        raise TypeError

    return float(current_event_vars.get(name, 0))

# Pure Python function
def getCurrentEventVarInt(name):
    """Returns the value of a named event variable in integer form."""
    if not isinstance(name, str):
        raise TypeError

    return int(current_event_vars.get(name, 0))

# Pure Python function
def getCurrentEventVarIsEmpty(name):
    """Returns 1 if the named event variable doesn't exist."""
    if not isinstance(name, str):
        raise TypeError

    return int(name not in current_event_vars)

# Pure Python function
def getCurrentEventVarString(name):
    """Returns the value of a named event variable in string form."""
    return getEventInfo(name)

# Pure Python function
def getEntityIndexes(classname=None):
    """Returns list of all entity indexes on the server, optionally filtered by a classname"""
    if classname is not None and not isinstance(classname, str):
        raise TypeError

    result = list()

    if classname is not None:
        generator = EntityGenerator(classname)
    else:
        generator = EntityGenerator()

    for edict in generator:
        result.append(index_from_edict(edict))

    return result

# Pure Python function
def getEventInfo(name):
    """Gets the value of a particular event variable."""
    if not isinstance(name, str):
        raise TypeError

    return str(current_event_vars.get(name, ''))

# Pure Python function
def getFlags(name):
    """Gets the flags value for a command"""
    if not isinstance(name, str):
        raise TypeError

    base = cvar.find_base(name)
    return base and base.flags

# Pure Python function
def getFloat(name):
    """Gets the float value for a server variable"""
    if not isinstance(name, str):
        raise TypeError

    convar = cvar.find_var(name)
    return convar and convar.get_float()

# Pure Python function
def getHelpText(name):
    """Gets the help text for a console command or server variable."""
    if not isinstance(name, str):
        raise TypeError

    base = cvar.find_base(name)
    return base and base.help_text

# Pure Python function
def getInt(name):
    """Gets the int value for a server variable"""
    if not isinstance(name, str):
        raise TypeError

    convar = cvar.find_var(name)
    return convar and convar.get_int()

# Pure Python function
def getString(name):
    """Gets the string value for a server variable"""
    if not isinstance(name, str):
        raise TypeError

    convar = cvar.find_var(name)
    return '' if convar is None else convar.get_string()

# Pure Python function
def getUseridList(*args):
    """Returns a list of the userids of all players on the server."""
    result = list()
    for player in PlayerGenerator():
        result.append(userid_from_edict(player))

    return result

@command
def getargc(argv):
    """Gets the count of parameters passed to the current ES console command."""
    return command_info.argc

@command
def getargs(argv):
    """Gets the commandstring passed to the current ES console command."""
    return command_info.args

@command
def getargv(argv):
    """Gets the command parameter passed to the current ES console command."""
    return command_info.get_argv(atoi(argv[1]))

@command
def getclientvar(argv):
    """Reads a console variable from a given player."""
    userid = argv[1]
    try:
        index = index_from_userid(atoi(userid))
    except ValueError:
        dbgmsg(0, 'userid not found: {}'.format(userid))
        _set_last_error('Userid not valid')
        return

    return engine_server.get_client_convar_value(index, argv[2]) or ''

# Not pure Python (console command is registered differently)
def getcmduserid(*args):
    """Gets the commandstring passed to the current Valve console command."""
    return command_info.userid

@command
def getentityindex(argv):
    """Gets the index for the first named entity found by that name. Returns -1 if not found."""
    classname = argv[1]
    entity = Entity.find(classname)
    return -1 if entity is None else entity.index

@command
def getentitypropoffset(argv):
    """Gets a server class property for a particular entity index"""
    try:
        pointer = pointer_from_index(atoi(argv[1]))
    except ValueError:
        return

    offset = atoi(argv[2])
    prop_type = atoi(argv[3])
    if prop_type == SendPropType.INT:
        return pointer.get_int(offset)

    if prop_type == SendPropType.FLOAT:
        return pointer.get_float(offset)

    if prop_type == SendPropType.VECTOR:
        return ','.join(map(str, memory.make_object(Vector, pointer + offset)))

    return None

@command
def getgame(argv):
    """Returns the name of the Source game being played."""
    return server_game_dll.game_description

@command
def getgravityvector(argv):
    """Returns the gravity vector."""
    env = physics.get_active_environment_by_index(0)
    if env is None:
        dbgmsg(0, 'No physics environment.')
        return None

    gravity = env.gravity
    dbgmsg(1, 'gravity: {}, {}, {}'.format(*gravity))
    return createvectorstring(*gravity)

@command
def gethandlefromindex(argv):
    """Gets the handle for an entity from its integer index."""
    try:
        return inthandle_from_index(atoi(argv[1]))
    except ValueError:
        return 0

@command
def getindexfromhandle(argv):
    """Gets the index for an entity from its integer handle."""
    try:
        return index_from_inthandle(atoi(argv[1]))
    except ValueError:
        return 0

@command
def getindexprop(argv):
    """Gets a server class property for a particular entity index"""
    try:
        entity = BaseEntity(atoi(argv[1]))
    except ValueError:
        return

    prop_type, offset = _get_prop_info(argv[2])
    if prop_type is None:
        return None

    ptr = entity.pointer
    if prop_type == SendPropType.INT:
        return ptr.get_int(offset)

    if prop_type == SendPropType.FLOAT:
        return ptr.get_float(offset)

    if prop_type == SendPropType.VECTOR:
        return ','.join(map(str, memory.make_object(Vector, ptr + offset)))

    if prop_type == SendPropType.STRING:
        return ptr.get_string(offset)

    return None

@command
def getlivingplayercount(argv):
    """Stores the count of living players on the server into a variable. Optionally a team can be specified. Returns -1 on error."""
    if len(argv) < 1 or len(argv) > 2:
        dbgmsg(0, 'Syntax: es_xgetplayercount <var> [team number]')
        _set_last_error('Not enough arguments.')
        return

    if len(argv) == 0:
        team = None
    else:
        team = atoi(argv[1])

    count = 0
    for player in PlayerIter():
        if _is_dead(player):
            continue

        if team is None:
            count += 1
        elif team == player.team:
            count += 1

    return count

@command
def getmaxplayercount(argv):
    """Stores the maximum number of player slots the server allows."""
    return global_vars.max_clients

@command
def getplayercount(argv):
    """Stores the count of players on the server into a variable. Optionally a team can be specified. Returns -1 on error."""
    if len(argv) < 1 or len(argv) > 2:
        dbgmsg(0, 'Syntax: es_xgetplayercount <var> [team number]')
        _set_last_error('Not enough arguments.')
        return

    if len(argv) == 0:
        team = None
    else:
        team = atoi(argv[1])

    count = 0
    for player in PlayerIter():
        if team is None:
            count += 1
        elif team == player.team:
            count += 1

    return count

@command
def getplayerhandle(argv):
    """Gets the handle for a player class property using an entity handle (Untested)"""
    try:
        return Player.from_userid(atoi(argv[0])).inthandle
    except ValueError:
        return 0

@command
def getplayerlocation(argv):
    """Stores the player's current x, y, and z location (in 3 different variables or a 3-tuple in Python)."""
    userid = atoi(argv[1])
    if userid > 0:
        try:
            return tuple(Player.from_userid(userid).origin)
        except ValueError:
            return (0, 0, 0)

    dbgmsg(0, 'getplayerlocation, invalid userid')
    _set_last_error('Invalid userid')
    return None

@command
def getplayermovement(argv):
    """Stores the player's current forward movement value, side movement value, and upward movement value (in 3 different variables or Python 3-tuple)."""
    try:
        bcmd = Player.from_userid(atoi(argv[1])).playerinfo.last_user_command
    except ValueError:
        return None

    return bcmd and (bcmd.forward_move, bcmd.side_move, bcmd.up_move)

@command
def getplayername(argv):
    """Stores the player's name in the variable."""
    userid = atoi(argv[1])
    if userid > 0:
        try:
            return Player.from_userid(userid).name
        except ValueError:
            return 0
    else:
        dbgmsg(0, 'Invalid userid for getplayername.')
        _set_last_error('Invalid userid')

    return None

@command
def getplayerprop(argv):
    """Gets a server class property for a particular player"""
    userid = atoi(argv[1])
    if userid > 0:
        try:
            index = index_from_userid(userid)
        except ValueError:
            dbgmsg(0, 'Entity doesn\'t exist.')
            return

        return getindexprop(index, argv[2])

    dbgmsg(0, 'ERROR: Userid must be greater than 0.')
    _set_last_error('Invalid arguments')

@command
def getplayersteamid(argv):
    """Stores the player's STEAMID in the variable."""
    try:
        return Player.from_userid(atoi(argv[1])).steamid or ''
    except ValueError:
        return ''

@command
def getplayerteam(argv):
    """Stores the player's team # in the variable."""
    try:
        return Player.from_userid(atoi(argv[1])).team
    except ValueError:
        return 0

@command
def getpropoffset(argv):
    """Gets a server class property offset for a particular property path"""
    prop_type, offset = _get_prop_info(argv[1])
    return 0 if offset is None else offset

@command
def getproptype(argv):
    """Gets a server class property type for a particular property path"""
    prop_type, offset = _get_prop_info(argv[1])
    return 0 if prop_type is None else int(prop_type)

@command
def getuserid(argv):
    """Looks-up a userid based on the string provided. Checks it against a userid, steamid, exact name, and partial name. (Based on Mani's algorithm.)"""
    if len(argv) == 1:
        dbgmsg(1, 'FindUserIDByString: Look for any connected player')
        for player in PlayerIter():
            return player.userid

        return 0

    target_string = argv[1]
    dbgmsg(1, 'FindUserIDByString: let\'s try to match this: {}'.format(target_string))

    # Search for UserID
    dbgmsg(1, 'FindUserIDByString: is it a userid?')
    target_userid = atoi(argv[1])
    if target_userid != 0:
        dbgmsg(1, 'FindUserIDByString: Probably is a userid.')
        try:
            edict_from_userid(target_userid)
        except ValueError:
            pass
        else:
            dbgmsg(1, 'FindUserIDByString: Yep, it\'s a userid.')
            return target_userid

        dbgmsg(1, 'FindUserIDByString: Hmm, maybe it\'s a handle?')
        try:
            result = userid_from_inthandle(target_userid)
        except ValueError:
            dbgmsg(1, 'FindUserIDByString: Not a handle or userid.')
        else:
            dbgmsg(1, 'FindUserIDByString: Yep, it\'s a handle.')
            return result

    # Search for SteamID
    dbgmsg(1, 'FindUserIDByString: is it a steamid?')

    # The next line is the original ES behaviour. It doesn't work with SteamID3
    #if len(target_string) > 6 and target_string.startswith('STEAM_'):
    if not target_string.isdigit() and SteamID.parse(target_string) is not None:
        dbgmsg(1, 'FindUserIDByString: really looks like a steamid.')
        for player in PlayerIter():
            if player.steamid == target_string:
                dbgmsg(1, 'FindUserIDByString: was a steamid')
                return player.userid

    # Search for exact name
    dbgmsg(1, 'FindUserIDByString: Look for exact name?')
    for player in PlayerIter():
        if player.name == target_string:
            dbgmsg(1, 'FindUserIDByString: found exact name')
            return player.userid

        dbgmsg(1, 'FindUserIDByString: not an exact name')

    # Search for exact name (case-insensitive)
    dbgmsg(1, 'FindUserIDByString: is there a name case-insensitive?')
    for player in PlayerIter():
        if player.name.lower() == target_string.lower():
            dbgmsg(1, 'FindUserIDByString: yep, there\'s a name case-insensitive!')
            return player.userid

    dbgmsg(1, 'FindUserIDByString: is it a BOT steamid?')
    if target_string == 'BOT':
        dbgmsg(1, 'FindUserIDByString: really looks like a BOT steamid.')
        for player in PlayerIter('bot'):
            dbgmsg(1, 'FindUserIDByString: was a steamid')
            return player.userid

    # Search for partial name
    dbgmsg(1, 'FindUserIDByString: is it a part of their name!')
    for player in PlayerIter():
        if target_string.lower() in player.name.lower():
            dbgmsg(1, 'FindUserIDByString: it is a part of their name: {}'.format(player.name))
            return player.userid

        dbgmsg(1, 'FindUserIDByString: didn\'t match: {}'.format(player.name))

    dbgmsg(1, 'FindUserIDByString: not found! {}'.format(target_string))
    return 0

@command
def give(argv):
    """Gives the player a named item."""
    try:
        player = Player.from_userid(atoi(argv[1]))
    except ValueError:
        return

    entity = argv[2]
    if not entity:
        return

    with _last_give_enabled(entity):
        _exec_client_cheat_command(player, 'give {}'.format(entity))

@command
def isbot(argv):
    """Checks a userid to see if it's a bot, stores 1 in the variable if so, 0 if not."""
    try:
        return int(Player.from_userid(atoi(argv[1])).is_fake_client())
    except ValueError:
        return None

@command
def isdedicated():
    """Returns 1 in the variable if the server a dedicated server."""
    return engine_server.is_dedicated_server()

@command
def keycreate(argv):
    """Creates a key that can be free-floating or associated with a group. Must call es_keydelete to free this memory when you're done."""
    group, key_name = _find_group(argv)
    if group is None:
        return

    new_key = group.find_key(key_name, True)
    if new_key is None:
        dbgmsg(0, 'ERROR: Eventscripts cannot find/create the {} key!'.format(key_name))
        _set_last_error('Key could not be found or created')

@command
def keydelete(argv):
    """Deletes a key from memory so that it's not leaked when you're done with it."""
    group, key_name = _find_group(argv)
    if group is None:
        return

    new_key = group.find_key(key_name)
    if new_key is None:
        dbgmsg(0, 'ERROR: Eventscripts cannot find the {} key!'.format(key_name))
        _set_last_error('Key could not be found or created')
    else:
        group.remove_sub_key(new_key)

@command
def keygetvalue(argv):
    """Gets a value within a given key (where the key could be free-floating or associated with a group)."""
    if len(argv) == 5:
        group = user_groups.find_key(argv[2])
        if group is None:
            dbgmsg(0, 'ERROR: Eventscripts cannot find the {} group!'.format(argv[2]))
            _set_last_error('Keygroup not found')
            return None

        key_name = argv[3]
        value_name = argv[4]
    else:
        group = ungrouped
        key_name = argv[2]
        value_name = argv[3]

    new_key = group.find_key(key_name)
    if new_key is None:
        keynum = atoi(key_name)
        if keynum > 0:
            new_key = group.first_true_sub_key
            for x in range(keynum):
                new_key = new_key.next_true_sub_key

        if new_key is None:
            dbgmsg(0, 'ERROR: Eventscripts cannot find the {} key!'.format(key_name))
            _set_last_error('Key not found')
            return None

    return new_key.get_string(value_name)

@command
def keygroupcopy(argv):
    """Copies a keygroup."""
    group = user_groups.find_key(argv[1])
    if group is None:
        dbgmsg(0, 'ERROR: Eventscripts cannot find the {} group!'.format(argv[1]))
        _set_last_error('Key not found')
        return

    new_group = group.make_copy()
    new_group.name = argv[2]
    new_group.next_key = group.next_key
    group.next_key = new_group

@command
def keygroupcreate(argv):
    """Creates a keygroup that can be loaded and saved to a file. Must call es_keygroupdelete to free this memory!"""
    new_group = user_groups.find_key(argv[1], True)
    if new_group is None:
        dbgmsg(0, 'ERROR: EventScripts couldn\'t create the user group.')

@command
def keygroupdelete(argv):
    """Deletes a keygroup from memory so that it's not leaked."""
    new_group = user_groups.find_key(argv[1])
    if new_group is None:
        dbgmsg(1, 'EventScripts couldn\'t find the user group {}'.format(argv[1]))
        return

    user_groups.remove_sub_key(new_group)

@command
def keygroupfilter(argv):
    """Deletes keys from a keygroup that match or don't match a certain value."""
    if len(argv) > 4:
        group = user_groups.find_key(argv[1])
        if group is None:
            dbgmsg(0, 'ERROR: Eventscripts cannot find the {} group!'.format(argv[1]))
            _set_last_error('Keygroup not found')
            return

        op = argv[2]
        value_name = argv[3]
        value_data = argv[4]
    else:
        group = ungrouped
        op = argv[1]
        value_name = argv[2]
        value_data = argv[3]

    # Filter here
    only = op.lower() == 'only'
    key = group.first_true_sub_key
    while key:
        found = False
        value = key.first_value
        while value:
            if value.get_string().lower() == value_data.lower() and value.name == value_name:
                found = True
                break

            value = value.next_value

        if found:
            if only:
                key = key.next_true_sub_key
            else:
                temp = key
                key = key.next_true_sub_key
                group.remove_sub_key(temp)
        else:
            if only:
                temp = key
                key = key.next_true_sub_key
                group.remove_sub_key(temp)
            else:
                key = key.next_true_sub_key

# Pure Python function
def keygroupgetpointer(string):
    """Returns the C++ pointer to a keygroup."""
    if not isinstance(string, str):
        raise TypeError

    key = user_groups.find_key(string)
    return 0 if key is None else _get_keyvalues_ptr(key)

@command
def keygroupload(argv):
    """Loads a keygroup from file based on its name."""
    full_path = _get_full_path(argv)
    new_group = user_groups.find_key(argv[1], True)
    if not new_group.load_from_file2(full_path):
        dbgmsg(0, 'ERROR: Could not load keygroup: {}!'.format(full_path))
        _set_last_error('Keygroup not found')

    dbgmsg(1, 'Loaded: {}'.format(full_path))

@command
def keygroupmsg(argv):
    """Sends a keygroup-based message to a player."""
    userid = argv[1]
    try:
        edict = edict_from_userid(atoi(userid))
    except ValueError:
        dbgmsg(0, 'Invalid userid: {}'.format(userid))
        return

    key_group_name = argv[3]
    kv = user_groups.find_key(key_group_name)
    if kv is None:
        dbgmsg(0, 'Error: KeyGroup {} not found.'.format(key_group_name))
        return

    key_msg = kv.find_key('message')
    if key_msg is None:
        dbgmsg(0, 'Error: \'message\' subkey was not found inside keygroup {}'.format(key_group_name))
        return

    create_message(edict, atoi(argv[2]), key_msg)

@command
def keygrouprename(argv):
    """Renames an existing keygroup."""
    new_group = user_groups.find_key(argv[1])
    if new_group is None:
        dbgmsg(0, 'EventScripts couldn\'t find the user group {}'.format(argv[1]))
        _set_last_error('Key not found')
        return

    new_group.name = argv[2]

@command
def keygroupsave(argv):
    """Saves a keygroup to a file based on its name."""
    full_path = _get_full_path(argv)
    new_group = user_groups.find_key(argv[1])
    if new_group is None:
        dbgmsg(0, 'EventScripts couldn\'t find the user group {}'.format(argv[1]))
        _set_last_error('Key not found')
        return

    if not new_group.save_to_file(full_path):
        dbgmsg(0, 'ERROR: Could not save keygroup file: {}'.format(full_path))
        _set_last_error('Keygroup could not be saved')

    dbgmsg(1, 'Saved: {}'.format(full_path))

@command
def keylist(argv):
    """Lists all key values in memory that aren't groups. Optionally can look up a group, if you provide one."""
    if len(argv) == 2:
        group = user_groups.find_key(argv[1])
        if group is None:
            dbgmsg(0, 'ERROR: Eventscripts cannot find the {} group!'.format(argv[1]))
            _set_last_error('Key not found')
            return
    else:
        group = ungrouped

    dbgmsg(0, '----------------------')
    key = group.first_true_sub_key
    while key:
        dbgmsg(0, 'Key: {}'.format(key.name))
        value = key.first_value
        while value:
            dbgmsg(0, '   Name: {}\n  Value: {}'.format(value.name, value.get_string()))
            value = value.next_value

        key = key.next_true_sub_key

    dbgmsg(0, '----------------------')

# Pure Python function
def keypcreate(*args):
    """Returns the C++ pointer to a new keyvalues object."""
    return _store_key_value(KeyValues(None))

# Pure Python function
def keypcreatesubkey(key_ptr):
    """Creates a subkey as an integer."""
    if not isinstance(key_ptr, int):
        raise TypeError

    if not key_ptr:
        return None

    new_key = _make_key_values(key_ptr).create_new_key()
    return new_key and _get_keyvalues_ptr(new_key)

# Pure Python function
def keypdelete(key_ptr):
    """Deletes a key by pointer (not recommended)"""
    if not isinstance(key_ptr, int):
        raise TypeError

    if not key_ptr:
        return None

    _remove_key_value(key_ptr)

# Pure Python function
def keypdetachsubkey(key_ptr, key_to_remove_ptr):
    """Detaches a subkey by pointer."""
    if not isinstance(key_ptr, int) or not isinstance(key_to_remove_ptr, int):
        raise TypeError

    if not key_ptr and not key_to_remove_ptr:
        return

    key = _make_keyvalues(key_ptr)
    key_to_remove = _make_keyvalues(key_to_remove_ptr)
    key.remove_sub_key(key_to_remove)

# Pure Python function
def keypfindsubkey(key_ptr, string, create):
    """Finds or creates a subkey by a particular name."""
    if (not isinstance(key_ptr, int) or not isinstance(string, str)
            or not isinstance(create, (int, bool))):
        raise TypeError

    if not key_ptr:
        return None

    key = _make_keyvalues(key_ptr)
    new_key = key.find_key(string, create)
    return new_key and _get_keyvalues_ptr(new_key)

# Pure Python function
def keypgetdatatype(key_ptr):
    """Returns the data type id of the value in the key."""
    if not isinstance(key_ptr, int):
        raise TypeError

    if not key_ptr:
        return None

    return _make_keyvalues(key_ptr).get_data_type(None)

# Pure Python function
def keypgetfirstsubkey(key_ptr):
    """Retrieves the first subkey underneath this pointer"""
    if not isinstance(key_ptr, int):
        raise TypeError

    if not key_ptr:
        return None

    return _get_keyvalues_ptr(_make_keyvalues(key_ptr).first_sub_key)

# Pure Python function
def keypgetfirsttruesubkey(key_ptr):
    """Retrieves the first true subkey for this pointer."""
    if not isinstance(key_ptr, int):
        raise TypeError

    if not key_ptr:
        return None

    return _get_keyvalues_ptr(_make_keyvalues(key_ptr).first_true_sub_key)

# Pure Python function
def keypgetfirstvaluekey(key_ptr):
    """Retrieves the first value in this pointer."""
    if not isinstance(key_ptr, int):
        raise TypeError

    if not key_ptr:
        return None

    return _get_keyvalues_ptr(_make_keyvalues(key_ptr).first_value)

# Pure Python function
def keypgetfloat(key_ptr, string):
    """Retrieves the float value in this pointer by name."""
    if not isinstance(key_ptr, int) or not isinstance(string, str):
        raise TypeError

    if not key_ptr:
        return None

    return _make_keyvalues(key_ptr).get_float(string)

# Pure Python function
def keypgetint(key_ptr, string):
    """Retrieves the int value in this pointer by name."""
    if not isinstance(key_ptr, int) or not isinstance(string, str):
        raise TypeError

    if not key_ptr:
        return None

    return _make_keyvalues(key_ptr).get_int(string)

# Pure Python function
def keypgetname(key_ptr):
    """Gets a key name by pointer"""
    if not isinstance(key_ptr, int):
        raise TypeError

    if not key_ptr:
        return None

    return _make_keyvalues(key_ptr).name

# Pure Python function
def keypgetnextkey(key_ptr):
    """Retrieves the next key (peer) to this pointer."""
    if not isinstance(key_ptr, int):
        raise TypeError

    if not key_ptr:
        return None

    return _get_keyvalues_ptr(_make_keyvalues(key_ptr).next_key)

# Pure Python function
def keypgetnexttruesubkey(key_ptr):
    """Retrieves the next true subkey to this pointer (ignores 'values')"""
    if not isinstance(key_ptr, int):
        raise TypeError

    if not key_ptr:
        return None

    return _get_keyvalues_ptr(_make_keyvalues(key_ptr).next_true_sub_key)

# Pure Python function
def keypgetnextvaluekey(key_ptr):
    """Retrieves the next value in this pointer."""
    if not isinstance(key_ptr, int):
        raise TypeError

    if not key_ptr:
        return None

    return _get_keyvalues_ptr(_make_keyvalues(key_ptr).next_value)

# Pure Python function
def keypgetstring(key_ptr, string):
    """Retrieves the string value in this pointer by name."""
    if not isinstance(key_ptr, int) or not isinstance(string, str):
        raise TypeError

    if not key_ptr:
        return None

    return _make_keyvalues(key_ptr).get_string(string)

# Pure Python function
def keypisempty(key_ptr):
    """Check if the keyvalue pointer is empty."""
    if not isinstance(key_ptr, int):
        raise TypeError

    if not key_ptr:
        return None

    return int(_make_keyvalues(key_ptr).is_empty())

# Pure Python function
def keyploadfromfile(key_ptr, string):
    """Saves the keyvalue pointer to filepath with all subkeys and values"""
    if not isinstance(key_ptr, int) or not isinstance(string, str):
        raise TypeError

    if key_ptr:
        _make_keyvalues(key_ptr).load_from_file2(string)

# Pure Python function
def keyprecursivekeycopy(key_ptr, key_source_ptr):
    """Recursively copies a key into another key"""
    if not isinstance(key_ptr, int) or not isinstance(key_source_ptr, int):
        raise TypeError

    if key_ptr and key_source_ptr:
        # TODO: Expose RecursiveCopyKeyValues()
        _make_keyvalues(key_ptr).recursive_copy(
            _make_keyvalues(key_source_ptr))

# Pure Python function
def keypsavetofile(key_ptr, string):
    """Saves the keyvalue pointer to filepath with all subkeys and values"""
    if not isinstance(key_ptr, int) or not isinstance(string, str):
        raise TypeError

    if key_ptr:
        _make_keyvalues(key_ptr).save_from_file(string)

# Pure Python function
def keypsetfloat(key_ptr, string, value):
    """Sets the float value in this pointer by name."""
    if (not isinstance(key_ptr, int) or not isinstance(string, str)
            or not isinstance(value, (int, float))):
        raise TypeError

    if key_ptr:
        _make_keyvalues(key_ptr).set_float(string, value)

# Pure Python function
def keypsetint(key_ptr, string, value):
    """Sets the int value in this pointer by name."""
    if (not isinstance(key_ptr, int) or not isinstance(string, str)
            or not isinstance(value, int)):
        raise TypeError

    if key_ptr:
        _make_keyvalues(key_ptr).set_int(string, value)

# Pure Python function
def keypsetname(key_ptr, name):
    """Sets a key name by pointer"""
    if not isinstance(key_ptr, int) or not isinstance(name, str):
        raise TypeError

    if key_ptr:
        _make_keyvalues(key_ptr).name = name

# Pure Python function
def keypsetstring(key_ptr, string, value):
    """Sets the string value in this pointer by name."""
    if (not isinstance(key_ptr, int) or not isinstance(string, str)
            or not isinstance(value, int)):
        raise TypeError

    if key_ptr:
        _make_keyvalues(key_ptr).set_string(string, value)

@command
def keyrename(argv):
    """Rename a key."""
    if len(argv) == 4:
        group = user_groups.find_key(argv[1])
        if group is None:
            dbgmsg(0, 'ERROR: Eventscripts cannot find the {} group!'.format(argv[1]))
            _set_last_error('Keygroup not found')
            return

        key_name = argv[2]
    else:
        group = ungrouped
        key_name = argv[1]

    new_key = group.find_key(key_name)
    if new_key is None:
        dbgmsg(0, 'ERROR: Eventscripts cannot find the {} key.'.format(key_name))
        _set_last_error('Key not found')
        return

    new_key.name = argv[3] if len(argv) == 4 else argv[2]

@command
def keysetvalue(argv):
    """Sets a value within a given key (where the key could be free-floating or associated with a group)."""
    if len(argv) == 5:
        group = user_groups.find_key(argv[1])
        if group is None:
            dbgmsg(0, 'ERROR: Eventscripts cannot find the {} group!'.format(argv[1]))
            _set_last_error('Keygroup not found')
            return

        key_name = argv[2]
        value_name = argv[3]
        value = argv[4]
    else:
        group = ungrouped
        key_name = argv[1]
        value_name = argv[2]
        value = argv[3]

    new_key = group.find_key(key_name)
    if new_key is None:
        dbgmsg(0, 'ERROR: Eventscripts cannot find/create the {} key!'.format(key_name))
        _set_last_error('Key could not be found or created')
        return

    new_key.set_string(value_name, value)
    dbgmsg(1, '{} key\'s {} value was set to {}.'.format(key_name, value_name, value))

@command
def lightstyle(argv):
    """Set light style."""
    style = atoi(argv[1])
    value = argv[2]
    engine_server.light_style(style, value)
    dbgmsg(1, 'Setting lightstyle: {}, {}'.format(style, value))

@command
def load(argv):
    """Loads a script or lists all loaded scripts if no script is provided."""
    import es
    if len(argv) < 2:
        es.printScriptList()
    else:
        addon_name = argv[1]

        # We can't load ES addons that have the same name like an SP plugin
        if plugin_manager.plugin_exists(addon_name):
            dbgmsg(0, '[EventScripts] ES addon has the same name like an SP plugin.')
        else:
            es.loadModuleAddon(argv[1])

@command
def loadevents(argv):
    """Reads an event file and registers EventScripts as a handler for those events."""
    pos = 1
    if len(argv) > 2:
        pos = 2
        game_event_manager.load_events_from_file(argv[pos])

    register_for_event_file(argv[pos])

@command
def log(argv):
    """Logs a message to the server log."""
    engine_server.log_print(argv.arg_string.replace('"', '') + '\n')

@command
def logv(argv):
    """Logs the text inside of a variable."""
    convar = cvar.find_var(argv[1])
    if convar is None:
        dbgmsg(0, 'ERROR: variable {} does not exist.'.format(argv[1]))
        _set_last_error('Variable does not exist')
    else:
        engine_server.log_print(convar.get_string() + '\n')

@command
def makepublic(argv):
    """Makes a console variable public such that changes to it are announced to clients."""
    convar_name = argv[1]
    convar = cvar.find_var(convar_name)
    if convar is None:
        dbgmsg(0, 'The var "{}" could not be found'.format(convar_name))
        _set_last_error('Variable couldn\'t be found.')
    else:
        convar.make_public()
        forcecallbacks(convar_name)

@command
def mathparse(argv):
    """Adds a say command that refers to a particular block."""
    convar_name = argv[1]
    convar = cvar.find_var(convar_name)
    if convar is None:
        dbgmsg(0, 'The var "{}" could not be set'.format(convar_name))
        _set_last_error('Variable does not exist')
        return

    if not _can_change(convar):
        return

    try:
        result = muparser.parse_expr(argv[2])
    except RuntimeError as e:
        dbgmsg(0, 'Exception: {}!'.format(e.args[0]))
    else:
        if result - int(result) != 0:
            convar.set_float(result)
        else:
            convar.set_string('%ld'% result)

@command
def menu(argv):
    """Sends an AMX-Style menu to the users"""
    showMenu(atoi(argv[1]), atoi(argv[2]), argv[3], argv[4])

@command
def msg(argv):
    """Broadcasts a message to all players. If the first word of the message is '#green', or '#lightgreen' then the message is displayed in that color, supports '#multi' also for embedded #green/#lightgreen in the message."""
    msg = _prepare_msg(argv, 1, 0)
    SayText2(msg).send()
    dbgmsg(0, msg)

def old_mexec(*args):
    """Runs an exec file from memory."""
    raise NotImplementedError

@command
def physics(argv):
    """Interface with the Source physics engine (physics gravity, object velocity, etc)."""
    env = physics.get_active_environment_by_index(0)
    if env is None:
        dbgmsg(0, 'ERROR: No physics environment.')
        _set_last_error('Internal error')
        return None

    operation = argv[1].lower()
    sub_operation = argv[2].lower()
    if operation == 'set':
        if sub_operation == 'gravity':
            gravity = splitvectorstring(argv[3])
            env.gravity = Vector(*gravity)
            dbgmsg(1, 'gravity: {}, {}, {}'.format(*gravity))
        elif sub_operation == 'airdensity':
            env.air_density = atof(argv[3])
    elif operation == 'get':
        if sub_operation == 'gravity':
            gravity = env.gravity
            dbgmsg(1, 'gravity: {}, {}, {}'.format(*gravity))
            return createvectorstring(*gravity)
        elif sub_operation == 'airdensity':
            return env.air_density
    elif operation == 'start':
        raise NotImplementedError
    elif operation == 'active':
        if sub_operation == 'teleport':
            obj = env.get_active_object_by_index(atoi(argv[3]))
            if obj is None:
                return

            # TOOD: Print address of "obj"
            dbgmsg(3, 'pObject: {}'.format(id(obj)))
            vec, ang = obj.position
            dbgmsg(3, 'Position: {}, {}, {}'.format(*vec))
            obj.set_position(Vector(*splitvectorstring(argv[4])), ang, True)
            dbgmsg(2, 'Teleported: {}.'.format(obj.game_index))
        elif sub_operation == 'setvelocity':
            obj = env.get_active_object_by_index(atoi(argv[3]))
            if obj is None:
                return

            # TOOD: Print address of "obj"
            dbgmsg(3, 'pObject: {}'.format(id(obj)))
            vel, ang_vel = obj.velocity
            dbgmsg(3, 'Position: {}, {}, {}'.format(*vel))
            obj.set_velocity_instantaneous(Vector(*splitvectorstring(argv[4])), ang_vel)
            dbgmsg(2, 'Set velocity: {}.'.format(obj.game_index))
        elif sub_operation == 'applyforce':
            obj = env.get_active_object_by_index(atoi(argv[3]))
            if obj is None:
                return

            # TOOD: Print address of "obj"
            dbgmsg(3, 'pObject: {}'.format(id(obj)))
            obj.apply_force_center(Vector(*splitvectorstring(argv[4])))
            dbgmsg(2, 'Set velocity: {}.'.format(obj.game_index))
        elif sub_operation == 'setmass':
            obj = env.get_active_object_by_index(atoi(argv[3]))
            if obj is not None:
                obj.mass = atof(argv[4])

@command
def playsound(argv):
    """Plays a sound to a player."""
    try:
        index = index_from_userid(atoi(argv[1]))
    except ValueError:
        return

    sound = argv[2]
    engine_sound.precache_sound(sound)
    engine_sound.emit_sound(
        RecipientFilter(index),
        index,
        0,
        sound,
        atof(argv[3]),
        1
    )

@command
def precachedecal(argv):
    """Precache a decal and return its index."""
    return engine_server.precache_decal(argv[1])

@command
def precachemodel(argv):
    """Precache a model and return its index."""
    return engine_server.precache_model(argv[1])

@command
def precachesound(argv):
    """Precache sound."""
    engine_sound.precache_sound(argv[1])

# Pure Python function
def printmsg(msg):
    """Outputs a message to the console."""
    if not isinstance(msg, str):
        raise TypeError

    Msg(msg)
    return 1

@command
def prop_dynamic_create(argv):
    """See prop_dynamic_create for syntax, but requires a userid first"""
    try:
        player = Player.from_userid(atoi(argv[1]))
    except ValueError:
        return

    with _last_give_enabled():
        _exec_client_cheat_command(
            player, 'prop_dynamic_create {}'.format(' '.join(argv.args[1:])))

@command
def prop_physics_create(argv):
    """See prop_physics_create for syntax, but requires a userid first."""
    try:
        player = Player.from_userid(atoi(argv[1]))
    except ValueError:
        return

    with _last_give_enabled():
        _exec_client_cheat_command(
            player, 'prop_physics_create {}'.format(' '.join(argv.args[1:])))

@command
def queryclientvar(argv):
    """Sends a request to query a client's console variable."""
    userid = atoi(argv[1])
    if userid > 0:
        try:
            engine_server.start_query_cvar_value(
                edict_from_userid(userid), argv[2])
        except ValueError:
            dbgmsg(0, 'Userid does not exist.')
            _set_last_error('Invalid userid')
    else:
        dbgmsg(0, 'Userid does not exist.')
        _set_last_error('Invalid userid')

@command
def queryregclientcmd(argv):
    """Queries which block a particular client cmd is pointed to."""
    command_str = argv[1]
    try:
        return client_command_proxies.get_proxy(command_str).block_name
    except KeyError:
        dbgmsg(2, 'es_xqueryregclientcmd: ERROR. Command {} doesn\'t exist.'.format(command_str))
        return ''

@command
def queryregcmd(argv):
    """Queries which block a console command refers to."""
    command_str = argv[1]
    try:
        return server_command_proxies.get_proxy(command_str).block_name
    except KeyError:
        dbgmsg(2, 'es_xqueryregcmd: ERROR. Command {} wasn\'t registered.'.format(command_str))
        return ''

@command
def queryregsaycmd(argv):
    """Queries which block a particular say cmd is pointed to."""
    command_str = argv[1]
    try:
        return say_command_proxies.get_proxy(command_str).block_name
    except KeyError:
        dbgmsg(2, 'es_xqueryregsaycmd: ERROR. Command {} wasn\'t registered.'.format(command_str))
        return ''

@command
def refreshpublicvars(argv):
    """Outputs all the console commands and variables."""
    current = cvar.commands
    while current:
        if not current.is_command() and current.is_flag_set(ConVarFlags.NOTIFY):
            cvar.call_global_change_callbacks(
                current, current.get_string(), current.get_float())

        current = current.next

@command
def regclientcmd(argv):
    """Adds a client command that refers to a particular block."""
    command_str = argv[1]
    if command_str in client_command_proxies:
        dbgmsg(0, 'Command {} already exists.'.format(command_str))
        return

    get_client_command(command_str).add_callback(
        client_command_proxies.create_proxy(command_str, argv[2]))

@command
def regcmd(argv):
    """Adds a console command that refers to a particular block."""
    command_str = argv[1]
    if cvar.find_command(command_str) is not None:
        dbgmsg(0, 'Command {} already exists.'.format(command_str))
        return

    get_server_command(command_str, argv[3]).add_callback(
        server_command_proxies.create_proxy(command_str, argv[2]))

def regex(*args):
    """Various regular expression commands."""
    raise NotImplementedError

@command
def regsaycmd(argv):
    """Adds a say command that refers to a particular block."""
    command_str = argv[1]
    if command_str in say_command_proxies:
        dbgmsg(0, 'Command {} already exists.'.format(command_str))
        return

    get_say_command(command_str).add_callback(
        say_command_proxies.create_proxy(command_str, argv[2]))

@command
def reload(argv):
    """Reloads a script that is loaded."""
    addon = argv[1]
    import es
    es.unloadModuleAddon(addon)
    es.loadModuleAddon(addon)

@command
def remove(argv):
    """Removes an entity class"""
    if len(argv) < 2:
        dbgmsg(0, 'Syntax: es_xremove <entity>')
        _set_last_error('Not enough arguments.')
        return

    with _cheats_enabled():
        ForceServerCommand('ent_remove {}'.format(argv[1]))

@command
def scriptpacklist(argv):
    """Lists the script packs running on the server. If a userid is provided, will es_tell the list to the user."""
    userid = 0
    if len(argv) > 1:
        userid = atoi(argv[1])

    _print_all_registered_cfg_scripts(userid)

# Pure Python command
def sendkeypmsg(userid, type, key_ptr):
    """Sends a client message based on a KeyValues pointer. sendkeypmsg(userid,type,keyid)"""
    if not isinstance(userid, int) or not isinstance(type, int) or not isinstance(key_ptr, int):
        raise TypeError

    try:
        edict = edict_from_userid(userid)
    except ValueError:
        dbgmsg(0, 'Error: "{}" is an invalid userid.'.format(userid))

    if not key_ptr:
        dbgmsg(0, 'Error: Invalid key for sending VGUI message.')

    create_message(edict, type, _make_keyvalues(key_ptr))

@command
def set(argv):
    """Adds/sets a new server/global variable."""
    name = argv[1]
    value = argv[2]
    if len(argv) > 3:
        _set_convar(name, value, True, argv[3])
    else:
        _set_convar(name, value, True)

# Pure Python function
def setFloat(name, value):
    """Sets the server variable to the given float value. Creating it if necessary."""
    if not isinstance(name, str) or not isinstance(value, float):
        raise TypeError

    convar = _set_convar(name, value, True)
    return convar and convar.get_float()

# Pure Python function
def setInt(name, value):
    """Sets the server variable to the given integer value. Creating it if necessary."""
    if not isinstance(name, str) or not isinstance(value, int):
        raise TypeError

    convar = _set_convar(name, value, True)
    return convar and convar.get_int()

# Pure Python function
def setNumRegistered(num):
    """Internal command for setting number of ticklisteners registered."""
    if not isinstance(num, int):
        raise TypeError

# Pure Python function
def setString(name, value):
    """Sets the server variable to the given string  value. Creating it if necessary."""
    if not isinstance(name, str) or not isinstance(value, str):
        raise TypeError

    convar = _set_convar(name, value, True)
    return convar and convar.get_string()

@command
def setang(argv):
    """Sets player view angle."""
    try:
        player = Player.from_userid(atoi(argv[1]))
    except ValueError:
        return

    _exec_client_cheat_command(
        player, 'setang {}'.format(' '.join(argv.args[1:])))

@command
def setentityname(argv):
    """Sets the targetname of an entity by index."""
    index = atoi(argv[1])
    try:
        BaseEntity(index).set_key_value_string('targetname', argv[2])
    except ValueError:
        dbgmsg(0, 'Could not set targetname for entity: {}'.format(index))

@command
def setentitypropoffset(argv):
    """Gets a server class property for a particular entity index"""
    try:
        pointer = pointer_from_index(atoi(argv[1]))
    except ValueError:
        return

    offset = atoi(argv[2])
    prop_type = atoi(argv[3])
    if prop_type == SendPropType.INT:
        pointer.set_int(atoi(argv[4]), offset)

    if prop_type == SendPropType.FLOAT:
        pointer.set_float(atof(argv[4]), offset)

    if prop_type == SendPropType.VECTOR:
        x, y, z = splitvectorstring(argv[4])
        ptr.set_float(x, offset + 0)
        ptr.set_float(y, offset + 4)
        ptr.set_float(z, offset + 8)

@command
def setindexprop(argv):
    """Sets a server class property for the given entity index"""
    try:
        entity = BaseEntity(atoi(argv[1]))
    except ValueError:
        return

    prop_type, offset = _get_prop_info(argv[2])
    if prop_type is None:
        return None

    value = argv[3]
    ptr = entity.pointer
    if prop_type == SendPropType.INT:
        ptr.set_int(atoi(value), offset)

    elif prop_type == SendPropType.FLOAT:
        ptr.set_float(atof(value), offset)

    elif prop_type == SendPropType.VECTOR:
        x, y, z = splitvectorstring(value)
        ptr.set_float(x, offset + 0)
        ptr.set_float(y, offset + 4)
        ptr.set_float(z, offset + 8)

@command
def setinfo(argv):
    """Adds a new server/global variable."""
    _set_convar(argv[1], argv[2], True)

@command
def setplayerprop(argv):
    """Sets a server class property for the given player"""
    try:
        index = index_from_userid(atoi(argv[1]))
    except ValueError:
        pass
    else:
        setindexprop(index, argv[2], argv[3])

@command
def setpos(argv):
    """Teleports a player."""
    try:
        player = Player.from_userid(atoi(argv[1]))
    except ValueError:
        return

    _exec_client_cheat_command(
        player, 'setpos {}'.format(' '.join(argv.args[1:])))

@command
def setview(argv):
    """Changes a players view to share that of a particular entity index."""
    try:
        player_edict = edict_from_userid(atoi(argv[1]))
    except ValueError:
        return

    if len(argv) > 2:
        try:
            view_edict = edict_from_index(atoi(argv[2]))
        except ValueError:
            return
    else:
        view_edict = player_edict

    engine_server.set_view(player_edict, view_edict)

@command
def sexec(argv):
    """Forces a userid to execute a command on the server console (bypassing client console)."""
    if 'jointeam' not in argv.arg_string:
        try:
            player = Player.from_userid(atoi(argv[1]))
        except ValueError:
            return

        player.client_command(argv.arg_string[len(argv[1]):].lstrip(), True)
    else:
        dbgmsg(0, 'jointeam not supported on bots')

@command
def sexec_all(argv):
    """Forces all users to execute a command on the server console."""
    if 'jointeam' in argv.arg_string:
        return

    for player in PlayerIter():
        player.client_command(argv.arg_string, True)

# Pure Python function
def showMenu(duration, userid, msg, options=''):
    """Sends an AMX-Style menu to the users"""
    userid = int(userid)
    if (not isinstance(duration, int)
            or not isinstance(msg, str)
            or not isinstance(options, str)):
        raise TypeError

    try:
        index = index_from_userid(userid)
    except ValueError:
        return

    duration = duration
    ShowMenu(
        msg,
        _get_menu_options(options),
        -1 if duration == 0 else duration
    ).send(index)

@command
def soon(argv):
    """Adds a command to the end of the command queue."""
    queue_command_string(argv.arg_string)

@command
def spawnentity(argv):
    """Spawn a given entity index."""
    index = atoi(argv[1])
    try:
        BaseEntity(index).spawn()
    except ValueError:
        es.dbgmsg(0, 'Could not spawn entity: {}'.format(index))

@command
def spawnplayer(argv):
    """Spawn a player with the given userid."""
    userid = argv[1]
    try:
        index = index_from_userid(atoi(userid))
    except ValueError:
        es.dbgms(0, 'Could not spawn userid: {}'.format(userid))
    else:
        try:
            BaseEntity(index).spawn()
        except ValueError:
            es.dbgmsg(0, 'Could not spawn entity: {}'.format(index))

@command
def splitvectorstring(argv):
    """Stores the vector's current x, y, and z as read from the vector in string form."""
    try:
        result = tuple(map(float, argv[1].split(',')))
    except ValueError:
        return (0.0, 0.0, 0.0)

    if len(result) != 3:
        return (0.0, 0.0, 0.0)

    return result

def sql(*args):
    """Local database support"""
    raise NotImplementedError

@command
def stopsound(argv):
    """Stops a specific sound for a player."""
    userid = atoi(argv[1])
    try:
        index = index_from_userid(userid)
    except ValueError:
        dbgmsg(0, 'StopSound: Unable to find player {}'.format(userid))
        return

    engine_sound.stop_sound(index, 0, argv[2])

@command
def stringtable(argv):
    """Update an entry in a stringtable"""
    table_name = argv[1]
    string = argv[2]
    table = string_tables[table_name]
    if table is None:
        dbgmsg(0, 'Could not add strings: {} to table {}'.format(
            string, table_name))
        return

    table.add_string(string, is_server=False, length=len(string)+1)
    dbgmsg(1, 'Added string: {} to table {}'.format(string, table_name))

@command
def tell(argv):
    """Sends HUD message to one player. If the first word of the message is '#green', or '#lightgreen' then the message is displayed in that color. Supports '#multi' also for embedded #green/#lightgreen in the message."""
    try:
        index = index_from_userid(atoi(argv[1]))
    except ValueError:
        return

    SayText2(_prepare_msg(argv, 2, 1)).send(index)

@command
def toptext(argv):
    """Sends HUD message to one player."""
    duration = atoi(argv[2])
    if duration < 1:
        dbgmsg(0, '{}: The duration of your message was set too low'.format(duration))
        return

    try:
        player = edict_from_userid(atoi(argv[1]))
    except ValueError:
        return

    msg = argv.arg_string[len(argv[1])+len(argv[2])+1:]
    msg = msg[2:] if msg[0] == '"' else msg[1:]

    color_str = ''
    for x in range(32):
        if x >= len(msg) or msg[x] == ' ':
            break

        color_str += msg[x]

    found, color = _color_from_string(color_str)
    if found:
        if len(msg) <= len(color_str):
            dbgmsg(0, 'You must send a message')
            return

        msg = msg[len(color_str)+1:]

    msg = msg.replace('"', '')
    data = KeyValues('msg')
    data.set_string('title', msg)
    data.set_color('color', color)
    data.set_int('level', 5)
    data.set_int('time', duration)
    create_message(player, DialogType.MSG, data)

@command
def trick(argv):
    """Miscellaneous tricky things."""
    operation = argv[1].lower()
    if operation == 'greenblock':
        try:
            player = Player.from_userid(atoi(argv[2]))
        except ValueError:
            return

        _exec_client_cheat_command(player, 'test_entity_blocker')

    elif operation == 'entity':
        with _last_give_enabled():
            with _cheats_enabled():
                ForceServerCommand('Test_CreateEntity {}'.format(argv[2]))

    elif operation == 'dispatcheffect':
        try:
            player = Player.from_userid(atoi(argv[2]))
        except ValueError:
            return

        _exec_client_cheat_command(
            player, 'test_dispatcheffect {} {} {} {}'.format(
                argv[3], argv[4], argv[5], argv[6]).rstrip())

@command
def unload(argv):
    """Unloads a script that has been loaded."""
    if len(argv) > 1:
        import es
        es.unloadModuleAddon(argv[1])

@command
def unregclientcmd(argv):
    """Removes a client command that refers to a particular block."""
    command_name = argv[1]
    try:
        proxy = client_command_proxies.pop(command_name)
    except KeyError:
        dbgmsg(0, 'unregclientcmd: Did not find command: {}'.format(command_name))
    else:
        get_client_command(command_name).remove_callback(proxy)

@command
def unregsaycmd(argv):
    """Removes a say command that refers to a particular block."""
    command_name = argv[1]
    try:
        proxy = say_command_proxies.pop(command_name)
    except KeyError:
        dbgmsg(0, 'unregsaycmd: Did not find command: {}'.format(command_name))
    else:
        get_say_command(command_name).remove_callback(proxy)

@command
def usermsg(argv):
    """Create and send a usermsg to a client."""
    if UserMessage.is_protobuf():
        raise UnsupportedOperation('This function is not supported with protobuf.')

    operation = argv[1].lower()

    if operation == 'create':
        if len(argv) > 3:
            msg_name = argv[2]
            msg_type_name = argv[3]
            try:
                data = _UserMessageData.data_store[msg_name]
            except KeyError:
                _UserMessageData.data_store[msg_name] = _UserMessageData(
                    msg_type_name)
            else:
                data.name = msg_type_name
        else:
            dbgmsg(0, 'Not enough parameters: {}'.format(argv.arg_string))

    elif operation == 'delete':
        if len(argv) > 2:
            msg_name = argv[2]
            try:
                del _UserMessageData.data_store[msg_name]
                dbgmsg(1, 'Key deleted: {}'.format(msg_name))
            except KeyError:
                pass

    elif operation == 'send':
        if len(argv) > 3:
            msg_name = argv[2]
            try:
                data = _UserMessageData.data_store[msg_name]
            except KeyError:
                dbgmsg(0, 'Key does not exist, please create it: {}'.format(
                    msg_name))
            else:
                data.send(argv[3])

    else:
        if len(argv) > 4:
            data_type, msg_name, value = (argv[2], argv[3], argv[4])
            if operation == 'write':
                _UserMessageData.write_user_message_data(
                    data_type, msg_name, value)

            elif operation == 'writev':
                convar = cvar.find_var(value)
                if convar is not None:
                    _UserMessageData.write_user_message_data(
                        data_type, msg_name, convar.get_string())
                else:
                    _UserMessageData.write_user_message_data(
                        data_type, msg_name, '0')
            else:
                dbgmsg(0, 'Unknown user message command: {}'.format(operation))
        else:
            dbgmsg(0, 'Not enough parameters: {}'.format(argv.arg_string))

@command
def voicechat(argv):
    """Allows you to control listening players."""
    try:
        to_index = index_from_userid(atoi(argv[2]))
    except ValueError:
        dbgmsg(0, 'Incorrect userids provided.')
        _set_last_error('Syntax Error')
        return

    try:
        from_index = index_from_userid(atoi(argv[3]))
    except ValueError:
        dbgmsg(0, 'Incorrect userids provided.')
        _set_last_error('Syntax Error')
        return

    operation = argv[1].lower()
    if operation == 'islistening':
        return int(voice_server.get_client_listening(to_index, from_index))
    elif operation == 'listen' or operation == 'nolisten':
        voice_server.set_client_listening(
            to_index, from_index, operation == 'listen')
