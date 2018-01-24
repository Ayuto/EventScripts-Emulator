# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import re

from contextlib import contextmanager
from ctypes.util import find_library

# Source.Python
#   Core
from core import PLATFORM
from core import SOURCE_ENGINE_BRANCH
#   Colors
from colors import Color
#   Cvars
from cvars import cvar
from cvars import ConVar
from cvars.flags import ConVarFlags
#   Commands
from commands import Command
#   Memory
import memory

from memory import Convention
from memory import DataType
from memory.manager import TypeManager
#   Engines
from engines.server import server_game_dll
#   Entities
from entities import EntityGenerator
from entities.props import SendPropType
from entities.helpers import index_from_edict
#   Players
from players.helpers import index_from_userid
from players.entity import Player
#   Filters
from filters.recipients import RecipientFilter
#   Messages
from messages import UserMessage
from messages import get_message_index

# ES Emulator
#   Cvars
from .cvars import botcexec_cvar
from .cvars import deadflag_cvar
from .cvars import lastgive_cvar
from .cvars import error_cvar
from .cvars import escape_cvar
#   Paths
from .paths import EMU_DATA_PATH


# =============================================================================
# >> __all__
# =============================================================================
__all__ = (
    '_prepare_msg',
    '_get_prop_info',
    'atoi',
    'atof',
    '_can_change',
    '_cexec',
    '_clamp',
    '_is_dead',
    '_get_send_prop_type_name',
    '_get_convar_flag',
    '_get_menu_options',
    '_dump_entity_table',
    '_exec_client_cheat_command',
    '_last_give_enabled',
    '_cheats_enabled',
    '_UserMessageData',
    '_get_convar',
    '_set_convar',
    'command',
    '_set_last_error',
    'Msg',
    '_color_from_string',
    '_print_all_registered_cfg_scripts',
    'UnsupportedOperation',
    'ConVar_'
)



# =============================================================================
# >> CONSTANTS
# =============================================================================
if SOURCE_ENGINE_BRANCH == 'csgo':
    COLOR_DEFAULT = '\1'
    COLOR_GREEN = '\4'
    COLOR_LIGHTGREEN = '\5'
    COLOR_DARKGREEN = '\6'
else:
    COLOR_DEFAULT = '\1'
    COLOR_GREEN = '\4'
    COLOR_LIGHTGREEN = '\3'
    COLOR_DARKGREEN = '\5'

RE_DEFAULT = re.compile('#default', re.IGNORECASE)
RE_GREEN = re.compile('#green', re.IGNORECASE)
RE_LIGHTGREEN = re.compile('#lightgreen', re.IGNORECASE)
RE_DARKGREEN = re.compile('#darkgreen', re.IGNORECASE)
RE_MULTI = re.compile('#multi', re.IGNORECASE)


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
NO_SRV_CHECK_GAMES = [
    'csgo'
]

if PLATFORM == 'windows':
    clib = memory.find_binary('msvcrt.dll')
    tier1 = memory.find_binary('bin/tier0')
else:
    clib_path = find_library('c')
    if clib_path is None:
        raise ValueError('Unable to find C library.')

    clib = memory.find_binary(clib_path, check_extension=False)
    tier1 = memory.find_binary(
        'bin/libtier0',
        SOURCE_ENGINE_BRANCH not in NO_SRV_CHECK_GAMES)

sv_cheats = cvar.find_var('sv_cheats')


# =============================================================================
# >> ConVar structure for es.forcevalue()
# =============================================================================
type_manager = TypeManager()
ConVar_ = type_manager.create_type_from_file(
    'ConVar_',
    EMU_DATA_PATH / 'memory' / 'ConVar_.ini')


# =============================================================================
# >> C FUNCTIONS
# =============================================================================
atoi = clib['atoi'].make_function(
    Convention.CDECL,
    [DataType.STRING],
    DataType.INT
)

atof = clib['atof'].make_function(
    Convention.CDECL,
    [DataType.STRING],
    DataType.FLOAT
)

Msg = tier1['Msg'].make_function(
    Convention.CDECL,
    [DataType.STRING],
    DataType.VOID
)


# =============================================================================
# >> EXCEPTIONS
# =============================================================================
class UnsupportedOperation(Exception):
    """Raise this exception if e. g. a function is and will not be supported."""


# =============================================================================
# >> HELPERS TO DECLARE ES FUNCTIONS
# =============================================================================
class PyCommand(Command):
    def __getitem__(self, index):
        # Restore default CCommand behaviour
        try:
            return super().__getitem__(index)
        except IndexError:
            return ''

    @property
    def args(self):
        return list(self[index] for index in range(1, len(self)))

def command(func):
    # TODO: Add all decorated functions to __all__
    def wrapper(*args):
        buffer = 'es_x{}'.format(func.__name__)
        for arg in args:
            arg = str(arg)
            buffer += ' '
            if any(x in arg for x in escape_cvar.get_string()) or '//' in arg:
                buffer += '"{}"'.format(arg)
            else:
                buffer += arg

        c = PyCommand()
        c.tokenize(buffer)
        import es
        es.dbgmsg(5, 'Command: {} {};'.format(c[0], c.arg_string))
        return func(c)
    return wrapper


# =============================================================================
# >> eventscripts_lasterror implementation
# =============================================================================
def _set_last_error(msg):
    error_cvar.set_string(msg)


# =============================================================================
# >> CONVAR HELPERS
# =============================================================================
def _get_convar(name, create=False, description='Custom server variable.'):
    convar = cvar.find_var(name)
    if convar is None:
        if create or autocreate_cvar.get_bool():
            return ConVar(name, '', description)
        else:
            import es
            es.dbgmsg(0, 'ERROR: Variable does not exist.')

    return convar

def _can_change(convar):
    # TODO: Implement
    return True

def _set_convar(name, value, create=False, description='Custom server variable.'):
    convar = _get_convar(name, create, description)
    if convar is not None:
        import es
        if _can_change(convar):
            convar.set_string(str(value))
            es.dbgmsg(4, '"{}" set to "{}"'.format(name, value))
        else:
            es.dbgmsg(1, 'Can\'t change variable: {}'.format(name))

    return convar


# =============================================================================
# >> HELPER TO PRINT ALL REGISTERED CFG SCRIPTS
# =============================================================================
def _print_all_registered_cfg_scripts(userid=0):
    import es
    from .logic import cfg_scripts

    if userid > 0:
        try:
            player = Player.from_userid(userid)
        except ValueError:
            return
    else:
        player = None

    header = 'EventScripts Script packs:'
    sep = '------------------------------------------'
    if player is not None:
        player.client_command('echo {}'.format(header))
        player.client_command('echo {}'.format(sep))
    else:
        es.dbgmsg(0, header)
        es.dbgmsg(0, sep)

    for index, (scriptpack, enabled) in enumerate(cfg_scripts.items()):
        msg = '{:02d}   {}   "{}"'.format(index, '[on]' if enabled else '[off]', scriptpack)
        if player is not None:
            player.client_command('echo {}'.format(msg))
        else:
            es.dbgmsg(0, msg)


    if player is not None:
        player.client_command('echo {}'.format(sep))
    else:
        es.dbgmsg(0, sep)


# =============================================================================
# >> es.msg() & es.tell()
# =============================================================================
def _prepare_msg(argv, color_index, skip):
    color_name = argv[color_index].lower()
    if color_name == '#green':
        msg = COLOR_GREEN + ' '.join(argv.args[color_index:])
    elif color_name == '#lightgreen':
        msg = COLOR_LIGHTGREEN + ' '.join(argv.args[color_index:])
    elif color_name == '#darkgreen':
        msg = COLOR_DARKGREEN + ' '.join(argv.args[color_index:])
    elif color_name == '#multi':
        msg = ' '.join(argv.args[color_index:])
        msg = RE_GREEN.sub(COLOR_GREEN, msg)
        msg = RE_LIGHTGREEN.sub(COLOR_LIGHTGREEN, msg)
        msg = RE_DARKGREEN.sub(COLOR_DARKGREEN, msg)
        msg = RE_DEFAULT.sub(COLOR_DEFAULT, msg)
    else:
        msg = ' '.join(argv.args[skip:])

    return msg


# =============================================================================
# >> es.toptext()
# =============================================================================
TOPTEXT_COLORS = {
    '#red': Color(255, 0, 0, 255),
    '#green': Color(0, 255, 0, 255),
    '#blue': Color(0, 0, 255, 255),
    '#orange': Color(255, 130, 0, 255),
    '#purple': Color(144, 0, 226, 255),
    '#violet': Color(144, 0, 226, 255),
    '#pink': Color(226, 0, 165, 255),
    '#cyan': Color(0, 255, 255, 255),
    '#yellow': Color(255, 255, 0, 255),
    '#white': Color(255, 255, 255, 255),
    '#black': Color(0, 0, 0, 255),
    '#darkgreen': Color(0, 145, 0, 255),
    '#darkblue': Color(0, 0, 145, 255),
    '#darkred': Color(145, 0, 0, 255),
    '#gray': Color(120, 120, 120, 255),
    '#grey': Color(120, 120, 120, 255),
}

def _color_from_string(string):
    try:
        return True, TOPTEXT_COLORS[string]
    except KeyError:
        return False, Color(255, 255, 255, 255)


# =============================================================================
# >> HELPERS FOR NETWORK PROPERTIES
# =============================================================================
_prop_info_cache = {}

def _get_prop_info(name):
    """Return the offset and the type of the given network property."""
    result = _prop_info_cache.get(name, None)
    if result is not None:
        return result

    splitted_path = name.split('.')
    classname = splitted_path.pop(0)

    result = (None, None)
    server_class = server_game_dll.all_server_classes
    while server_class:
        if server_class.name == classname:
            result = _get_prop_info_from_table(
                server_class.table, splitted_path)
            break

        server_class = server_class.next

    _prop_info_cache[name] = result
    return result

def _get_prop_info_from_table(table, prop_path, offset=0):
    if not prop_path:
        return (None, None)

    prop_name = prop_path.pop(0)
    for prop in table:
        if prop.name != prop_name:
            continue

        offset += prop.offset
        if not prop_path:
            return prop.type, offset

        return _get_prop_info_from_table(prop.data_table, prop_path, offset)

    return (None, None)


# =============================================================================
# >> es.dumpserverclasses()
# =============================================================================
SEND_PROP_TYPE_NAMES = {
    SendPropType.INT: 'int',
    SendPropType.FLOAT: 'float',
    SendPropType.VECTOR: 'vector',
    SendPropType.STRING: 'string',
    SendPropType.ARRAY: 'array',
    SendPropType.DATATABLE: 'int',
}

def _get_send_prop_type_name(prop_type):
    return SEND_PROP_TYPE_NAMES.get(prop_type, 'Unknown')


# =============================================================================
# >> es.dumpentities()
# =============================================================================
def _dump_entity_table(entity, table, path, offset=0):
    import es
    ptr = entity.pointer
    for prop in table:
        current_offset = offset + prop.offset
        current_path = '{}.{}'.format(path, prop.name)
        if prop.type == SendPropType.DATATABLE:
            _dump_entity_table(
                entity, prop.data_table, current_path, current_offset)
            continue

        if prop.type == SendPropType.INT:
            value = ptr.get_int(current_offset)
        elif prop.type == SendPropType.FLOAT:
            value = ptr.get_float(current_offset)
        elif prop.type == SendPropType.VECTOR:
            value = '{},{},{}'.format(
                ptr.get_float(), ptr.get_float(4), ptr.get_float(8))
        elif prop.type == SendPropType.STRING:
            # Not really a TODO for SP, but ES didn't implement it
            value = '(TODO: string)'
        elif prop.type == SendPropType.ARRAY:
            # Not really a TODO for SP, but ES didn't implement it
            value = '(TODO: array)'
        else:
            value = '(Unknown)'

        es.dbgmsg(0, '{} = {}'.format(current_path, value))


# =============================================================================
# >> es.cexec() & es.cexec_all()
# =============================================================================
def _cexec(player, command_str):
    if not player.is_fake_client():
        player.client_command(command_str)
    elif botcexec_cvar.get_int() > 0 and command_str == 'jointeam':
        player.client_command(command_str, True)


# =============================================================================
# >> eventscripts_deadflag
# =============================================================================
def _is_dead(player):
    if deadflag_cvar.get_int() > 0:
        return int(player.dead)

    return int(player.playerinfo.is_dead())


# =============================================================================
# >> es.flags()
# =============================================================================
CONVAR_FLAGS = {
    'cheat': ConVarFlags.CHEAT,
    'notify': ConVarFlags.NOTIFY,
    'gamedll': ConVarFlags.GAMEDLL,
    'replicated': ConVarFlags.REPLICATED,
    'protected': ConVarFlags.PROTECTED,
    'unlogged': ConVarFlags.UNLOGGED,
    'neverstring': ConVarFlags.NEVER_AS_STRING,
    'printable': ConVarFlags.PRINTABLEONLY,
    'dontrecord': ConVarFlags.DONTRECORD,
    'developmentonly': ConVarFlags.DEVELOPMENTONLY,
}

def _get_convar_flag(name):
    try:
        return CONVAR_FLAGS[name]
    except KeyError:
        return atoi(name)


# =============================================================================
# >> es.menu()
# =============================================================================
def _get_menu_options(keys):
    if not keys:
        return 1023

    result = 0
    for x in range(10):
        if str(x) in keys:
            result += 1 << x

    return result


# =============================================================================
# >> sv_cheats related commands
# =============================================================================
@contextmanager
def _cheats_enabled():
    """A nitfy context manager to enable sv_cheats temporarily."""
    old_value = sv_cheats.get_int()
    old_flags = sv_cheats.flags
    # Use try/finally to make sure sv_cheats is always set back to its
    # original value in case something went wrong.
    try:
        # Adding this flag will prevent ICvar::CallGlobalChangeCallbacks()
        # from being called. Thus, we don't need to remove the NOTIFY flag and
        # care about other side effects.
        sv_cheats.add_flags(ConVarFlags.NEVER_AS_STRING)
        sv_cheats.set_int(1)
        yield
    finally:
        sv_cheats.set_int(old_value)
        sv_cheats.flags = old_flags

def _get_entity_indexes(classname=''):
    result = set()
    for edict in EntityGenerator(classname, True):
        result.add(index_from_edict(edict))

    return result

@contextmanager
def _last_give_enabled(classname=''):
    lastgive_cvar.set_int(0)
    old_indexes = _get_entity_indexes(classname)
    yield
    new_indexes = _get_entity_indexes(classname)
    try:
        lastgive_cvar.set_int(new_indexes.difference(old_indexes).pop())
    except KeyError:
        pass

def _exec_client_cheat_command(player, command):
    with _cheats_enabled():
        player.client_command(command, True)


# =============================================================================
# >> es.usermsg
# =============================================================================
class _UserMessageData(list):
    data_store = {}

    def __init__(self, name):
        self.name = name

    @staticmethod
    def write_user_message_data(data_type, msg_name, value):
        try:
            data = _UserMessageData.data_store[msg_name]
        except KeyError:
            import es
            dbgmsg(0, 'Key does not exist, please create it: {}'.format(
                msg_name))
        else:
            data.append((data_type, value))

    def send(self, userid):
        msg_index = get_message_index(self.name)
        if msg_index == -1:
            import es
            dbgmsg(0, 'Invalid UserMessage type: {}'.format(self.name))
            return

        try:
            index = index_from_userid(atoi(userid))
        except ValueError:
            return

        # We need to save the RecipientFilter instance here. Otherwise it would
        # get garbage collected before it is send.
        recipients = RecipientFilter(index)
        user_message = UserMessage(recipients, self.name)
        buffer = user_message.buffer

        for type_name, value in self:
            self._write(buffer, type_name, value)

        user_message.send()

    @staticmethod
    def _write(buffer, type_name, value):
        type_name = type_name.lower()
        if type_name == 'string':
            buffer.write_string(str(value))
        elif type_name == 'float':
            buffer.write_float(atof(value))
        elif type_name == 'short':
            buffer.write_short(atoi(value))
        elif type_name == 'char':
            buffer.write_char(atoi(value))
        elif type_name == 'byte':
            buffer.write_byte(atoi(value))
        elif type_name == 'long':
            buffer.write_long(atoi(value))


# =============================================================================
# >> es.createplayerlist
# =============================================================================
def _clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)
