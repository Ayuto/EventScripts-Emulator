# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import re

# Source.Python
#   Cvars
from cvars.flags import ConVarFlags
#   Memory
import memory

from memory import Convention
from memory import DataType
#   Engines
from engines.server import server_game_dll
#   Entities
from entities.props import SendPropType

# ES Emulator
from .cvars import botcexec_cvar
from .cvars import deadflag_cvar


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# TODO: On Linux it's probably libc
runtimelib = memory.find_binary('msvcrt.dll')


# =============================================================================
# >> C FUNCTIONS
# =============================================================================
_atoi = runtimelib['atoi'].make_function(
    Convention.CDECL,
    [DataType.STRING],
    DataType.INT
)

def atoi(value):
    return _atoi(str(value))

_atof = runtimelib['atof'].make_function(
    Convention.CDECL,
    [DataType.STRING],
    DataType.FLOAT
)

def atof(value):
    return _atof(str(value))


# =============================================================================
# >> _prepare_msg
# =============================================================================
RE_DEFAULT = re.compile('#default', re.IGNORECASE)
RE_GREEN = re.compile('#green', re.IGNORECASE)
RE_LIGHTGREEN = re.compile('#lightgreen', re.IGNORECASE)
RE_DARKGREEN = re.compile('#darkgreen', re.IGNORECASE)
RE_MULTI = re.compile('#multi', re.IGNORECASE)

def _prepare_msg(color, msg):
    if msg is None:
        msg = color
    else:
        if RE_GREEN.match(color):
            msg = '\4' + msg
        elif RE_LIGHTGREEN.match(color):
            msg = '\3' + msg
        elif RE_DARKGREEN.match(color):
            msg = '\5' + msg
        elif RE_MULTI.match(color):
            msg = RE_GREEN.sub('\4', msg)
            msg = RE_LIGHTGREEN.sub('\3', msg)
            msg = RE_DARKGREEN.sub('\5', msg)
            msg = RE_DEFAULT.sub('\1', msg)

    return msg


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
# >> HELPERS FOR CEXEC
# =============================================================================
def _cexec(player, command_str):
    if not player.is_fake_client():
        player.client_command(command_str)
    elif botcexec_cvar.get_int() > 0 and command_str == 'jointeam':
        player.client_command(command_str, True)

def _is_dead(player):
    if deadflag_cvar.get_int() > 0:
        return player.dead

    return player.playerinfo.is_dead()


# =============================================================================
# >> HELPERS FOR SERVER CLASS DUMPS
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
# >> HELPERS FOR es.flags()
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