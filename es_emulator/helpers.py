# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import re

from contextlib import contextmanager

# Source.Python
#   Cvars
from cvars import cvar
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

sv_cheats = cvar.find_var('sv_cheats')


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
# >> es.msg() & es.tell()
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
        return player.dead

    return player.playerinfo.is_dead()


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
def cheats_enabled():
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

def exec_client_cheat_command(player, command):
    with cheats_enabled():
        player.client_command(command, True)
