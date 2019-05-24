# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import sys
import time
import muparser

# Source.Python
#   Core
from core import get_interface
#   Cvars
from cvars import cvar
from cvars.flags import ConVarFlags
from cvars import ConVar
#   Events
from events.manager import game_event_manager
from events.listener import GameEventListener
#   Engines
from engines.server import server
from engines.server import global_vars
from engines.server import QueryCvarStatus
from engines.server import queue_server_command
#   Listeners
from listeners import OnTick
from listeners import OnLevelInit
from listeners import OnNetworkidValidated
from listeners import OnClientSettingsChanged
from listeners import OnQueryCvarValueFinished
#   Players
from players.entity import Player
from players.helpers import userid_from_index
#   Commands
from commands import CommandReturn
from commands.say import SayFilter
from commands.client import ClientCommandFilter
from commands.server import ServerCommand
#   Paths
from paths import GAME_PATH
#   KeyValues
from keyvalues import KeyValues

# EventScripts Emulator
#   Cvars
from .cvars import noisy_cvar
from .cvars import currentmap_cvar
from .cvars import autorefreshvars_cvar
from .cvars import protectrcon_cvar
from .cvars import sayevents_cvar
from .cvars import nextmap_cvar
from .cvars import setipcmdline_cvar
from .cvars import frametimer_cvar
from .cvars import cmdprefix_cvar
from .cvars import scriptdir_cvar
from .cvars import execmd_cvar
from .cvars import defaultevents_cvar
from .cvars import mapcommands_cvar
from .cvars import serverdll_cvar
from .cvars import serverclients_cvar
#   Helpers
from .helpers import _is_dead
from .helpers import _set_last_error
#   Paths
from .paths import ES_EVENTS_PATH
from .paths import SERVER_BINARY


# =============================================================================
# >> COMMAND SYSTEM
# =============================================================================
class _CommandInfo(object):
    def __init__(self):
        self._args = ()
        self.userid = 0

    def get_argv(self, index):
        return self._args[index] if index < self.argc else ''

    @property
    def args(self):
        return ' '.join(self._args)

    @property
    def argc(self):
        return len(self._args)

    def set_args(self, command):
        self._args = tuple(command)

command_info = _CommandInfo()


class _CommandProxy(object):
    def __init__(self, block_name):
        self.block_name = block_name

    def __call__(self, command, index=None, team_only=None):
        command_info.set_args(command)
        if index is not None:
            command_info.userid = userid_from_index(index)

        import es
        es.addons.callBlock(self.block_name)


class _CommandProxies(dict):
    def create_proxy(self, command, block_name):
        instance = self[command] = _CommandProxy(block_name)
        return instance

    def get_proxy(self, command):
        return self[command]


server_command_proxies = _CommandProxies()
say_command_proxies = _CommandProxies()
client_command_proxies = _CommandProxies()


# =============================================================================
# >> EVENT SYSTEM
# =============================================================================
NOISY_EVENTS = (
    'weapon_reload',
    'player_footstep',
    'weapon_reload',
    'weapon_fire',
    'bullet_impact',
)

current_event_vars = {}
cfg_scripts = {}

def fill_event_vars(userid, type_str):
    try:
        player = Player.from_userid(userid)
    except ValueError:
        return

    current_event_vars['es_{}name'.format(type_str)] = player.name
    current_event_vars['es_{}steamid'.format(type_str)] = player.steamid
    current_event_vars['es_{}weapon'.format(type_str)] = player.playerinfo.weapon_name
    current_event_vars['es_{}team'.format(type_str)] = player.team
    current_event_vars['es_{}armor'.format(type_str)] = player.armor
    current_event_vars['es_{}health'.format(type_str)] = player.health
    current_event_vars['es_{}deaths'.format(type_str)] = player.deaths
    current_event_vars['es_{}kills'.format(type_str)] = player.kills
    current_event_vars['es_{}dead'.format(type_str)] = _is_dead(player)
    current_event_vars['es_{}index'.format(type_str)] = player.index

def exec_all_registered(event_name):
    import es

    exec_cmd = execmd_cvar.get_string()
    script_dir = scriptdir_cvar.get_string()

    # Execute root scripts
    cfg_path = '{}/{}.cfg'.format(script_dir, event_name)
    if GAME_PATH.joinpath('cfg', cfg_path).exists():
        es.dbgmsg(2, 'Sending {} command for {}.'.format(exec_cmd, event_name))
        queue_server_command(exec_cmd, cfg_path)

    # Execute cfg scripts
    es.dbgmsg(2, 'Script pack registration scanning...')
    for scriptpack, enabled in cfg_scripts.items():
        if not enabled:
            continue

        cfg_path = '{}/{}/{}.cfg'.format(script_dir, scriptpack, event_name)
        if GAME_PATH.joinpath('cfg', cfg_path).exists():
            es.dbgmsg(2, 'Sending {} command for {}.'.format(exec_cmd, cfg_path))
            queue_server_command(exec_cmd, cfg_path)
        else:
            es.dbgmsg(1, 'File doesn\'t exist: {}'.format(cfg_path))

    # Execute Python addons
    es.dbgmsg(2, 'Checking all scripts...')
    es.addons.triggerEvent(event_name)

def default_event_registration():
    import es

    es.dbgmsg(1, ' ** Registering files...')
    if not register_for_event_file('resource/modevents.res'):
        if not register_for_event_file('Resource/modevents.res'):
            es.dbgmsg(0, 'EventScripts] ERROR: Couldn\'t load modevents.res.')

    if not register_for_event_file('../hl2/resource/gameevents.res'):
        if not register_for_event_file('resource/gameevents.res'):
            es.dbgmsg(0, '[EventScripts] ERROR: Couldn\'t load gameevents.res.')

    if not register_for_event_file('../hl2/resource/serverevents.res'):
        if not register_for_event_file('resource/serverevents.res'):
            es.dbgmsg(0, '[EventScripts] ERROR: Couldn\'t load serverevents.res.')

    if not register_for_event_file(str(ES_EVENTS_PATH)):
        es.dbgmsg(0, 'ERROR: COULDN\'T LOAD MATTIE CORE EVENTS!')

    es.dbgmsg(1, ' ** Done registering default event files.')

class ESEventListener(GameEventListener):
    def fire_game_event(self, event):
        if noisy_cvar.get_int() != 1 and event.name in NOISY_EVENTS:
            return

        current_event_vars.clear()
        current_event_vars['es_event'] = event.name
        current_event_vars.update(event.variables.as_dict())

        userid = current_event_vars.get('userid', 0)
        if userid:
            fill_event_vars(userid, 'user')

        attacker = current_event_vars.get('attacker', 0)
        if attacker:
            fill_event_vars(attacker, 'attacker')

        exec_all_registered(event.name)

es_event_listener = ESEventListener()

def register_for_event_file(file_name):
    events = KeyValues.load_from_file(file_name)
    if events is None:
        _set_last_error('Couldn\'t load events file.')
        return False

    import es

    kv = events.first_sub_key
    while kv:
        es.dbgmsg(1, 'Added: {}'.format(kv.name))
        game_event_manager.add_listener(es_event_listener, kv.name, True)
        kv = kv.next_key

    es.dbgmsg(1, 'Done loading events.')
    return True


# =============================================================================
# >> CURRENT MAP & AUTO REFRESH PUBLIC CVARS
# =============================================================================
@OnLevelInit
def on_level_init(map_name):
    currentmap_cvar.set_string(map_name)
    if defaultevents_cvar.get_int() != 0:
        default_event_registration()

    event = game_event_manager.create_event('es_map_start')
    if event is not None:
        event.set_string('mapname', map_name)
        game_event_manager.fire_event(event)

    import es
    es.dbgmsg(3, 'es_map_start fired.')
    if autorefreshvars_cvar.get_int() > 0:
        es.refreshpublicvars()

    muparser.clear_vars()
    es.dbgmsg(6, ' Reset variables for muParser.')

currentmap_cvar.set_string(global_vars.map_name)

@OnNetworkidValidated
def on_network_id_validated(name, networkid):
    event = game_event_manager.create_event('es_player_validated')
    if event is not None:
        event.set_string('name', name)
        event.set_string('networkid', networkid)
        game_event_manager.fire_event(event)

@OnClientSettingsChanged
def on_client_settings_changed(index):
    event = game_event_manager.create_event('es_player_setting')
    if event is None:
        return

    client = server.get_client(index-1)
    if client is None:
        return

    event.set_int('userid', client.userid)
    game_event_manager.fire_event(event)

QUERY_STATUS = {
    QueryCvarStatus.SUCCESS: 'success',
    QueryCvarStatus.NOT_FOUND: 'not found',
    QueryCvarStatus.INVALID: 'not variable',
    QueryCvarStatus.PROTECTED: 'protected',
}

@OnQueryCvarValueFinished
def on_query_cvar_value_finished(cookie, index, status, cvar_name, cvar_value):
    event = game_event_manager.create_event('es_player_variable')
    if event is None:
        return

    try:
        userid = userid_from_index(index)
    except ValueError:
        userid = 0

    event.set_int('userid', userid)
    event.set_string('status', QUERY_STATUS.get(status, ''))
    event.set_string('variable', cvar_name)
    event.set_string('value', cvar_value)
    game_event_manager.fire_event(event)


# =============================================================================
# >> TICK LISTENER
# =============================================================================
@OnTick
def on_tick():
    now = time.time()

    import es
    es.addons.tick()

    if frametimer_cvar.get_int():
        diff = time.time() - now
        if diff > 0.01:
            es.dbgmsg(0, '[EventScripts] Long frame: {} seconds'.format(diff))


# =============================================================================
# >> SAY FILTER/COMMANDS
# =============================================================================
@SayFilter
def on_say(command, index, team_only):
    if sayevents_cvar.get_int() <= 0:
        return CommandReturn.CONTINUE

    import es

    try:
        userid = userid_from_index(index)
    except ValueError:
        userid = 0

    fire_es_player_chat(command, userid, team_only)

    # TODO: es.regsaycmd() should be handled here and not with SP's
    #       get_say_command()
    if es.addons.sayFilter(userid, command.arg_string, team_only):
        return CommandReturn.CONTINUE

    return CommandReturn.BLOCK

def fire_es_player_chat(command, userid, team_only):
    if len(command) <= 1:
        return

    event = game_event_manager.create_event('es_player_chat')
    if event is None:
        return

    event.set_int('userid', userid)
    event.set_bool('teamonly', team_only)

    full_text = command.arg_string
    if (userid > 0 and full_text[0] == '"'
            and full_text[-1] == '"'
            and full_text.count('"') <= 2):
        event.set_string('text', full_text[1:-1])
    else:
        event.set_string('text', full_text)

    game_event_manager.fire_event(event)


# =============================================================================
# >> CLIENT COMMAND FILTER & es_client_command
# =============================================================================
@ClientCommandFilter
def on_client_command(command, index):
    try:
        userid = userid_from_index(index)
    except ValueError:
        # Not sure when this happens... But if it happens, we don't want to
        # continue. See also:
        # https://forums.sourcepython.com/viewtopic.php?p=12943#p12943
        return CommandReturn.CONTINUE

    import es
    if not es.addons.clientCommand(userid):
        return CommandReturn.BLOCK

    command_name = command[0]
    fire_client_command = command_name[0] in cmdprefix_cvar.get_string()
    if fire_client_command or command_name == 'menuselect':
        event = game_event_manager.create_event('es_client_command', True)
        if event is not None:
            event.set_int('userid', userid)
            event.set_string('command', command_name)
            event.set_string('commandstring', command.arg_string)
            try:
                game_event_manager.fire_event(event)
            except RuntimeError:
                # TODO:
                # I have no idea why that happens, but the event gets fired...
                pass
        else:
            es.dbgmsg(0, 'es_client_command not fired! =(')

    return CommandReturn.CONTINUE


# =============================================================================
# >> RCON PASSWORD PROTECTION
# =============================================================================
if protectrcon_cvar.get_int() > 0:
    cvar.find_var('rcon_password').add_flags(ConVarFlags.PROTECTED)


# =============================================================================
# >> mattie_eventscripts.res
# =============================================================================
if game_event_manager.load_events_from_file(str(ES_EVENTS_PATH)) == 0:
    raise ValueError('Failed to load mattie_eventscripts.res')

if defaultevents_cvar.get_int() != 0:
    default_event_registration()


# =============================================================================
# >> eventscripts_setipcmdline
# =============================================================================
def check_ip_cmdline():
    if setipcmdline_cvar.get_int() <= 0:
        return

    try:
        index = sys.argv.index('+ip') + 1
    except ValueError:
        return

    try:
        ConVar('ip').set_string(sys.argv[index])
    except IndexError:
        pass
    else:
        import es
        es.dbgmsg(0, '[EventScripts] Temporary: Setting the host\'s IP variable from the command-line.')


# =============================================================================
# >> CHANGELEVEL HOOK
# =============================================================================
@ServerCommand('changelevel')
def on_changelevel(command):
    if mapcommands_cvar.get_int() <= 0:
        return

    new_map = nextmap_cvar.get_string()
    if new_map in ('', '0') or len(command) <= 1:
        return

    import es
    nextmap_cvar.set_string('')
    queue_server_command('changelevel', new_map)
    es.dbgmsg(0, '[EventScripts] Next map changed from {} to {}.'.format(
        command[1], new_map))
    return CommandReturn.BLOCK


# =============================================================================
# >> POST INITIALIZATION
# =============================================================================
def _muparser_parse_var(name):
    var = cvar.find_var(name)
    if var is None:
        return 0

    return var.get_float()

def _get_interface_version(interface, library, start_index):
    for index in range(start_index, 999):
        version = interface.format(index)
        try:
            get_interface(library, version)
            return version
        except ValueError:
            pass

    return None

def post_initialization():
    import es
    v = _get_interface_version('ServerGameDLL{:03d}', SERVER_BINARY, 3)
    if v is not None:
        es.dbgmsg(1, 'Using {} for game.'.format(v))
        serverdll_cvar.set_string(v)

    v = _get_interface_version('ServerGameClients{:03d}', SERVER_BINARY, 3)
    if v is not None:
        es.dbgmsg(1, 'Using {} for game.'.format(v))
        serverclients_cvar.set_string(v)

    check_ip_cmdline()
    muparser.init_parser(_muparser_parse_var)
