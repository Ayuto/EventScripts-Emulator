# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import sys
import time

# Source.Python
#   Cvars
from cvars import cvar
from cvars.flags import ConVarFlags
#   Memory
import memory

from memory.hooks import PreHook
#   Events
from events import GameEvent
from events.manager import game_event_manager
#   Engines
from engines.server import global_vars
from engines.server import engine_server
#   Listeners
from listeners import OnTick
from listeners import OnLevelInit
#   Players
from players.entity import Player
from players.helpers import userid_from_index
#   Commands
from commands import CommandReturn
from commands.say import SayFilter
from commands.client import ClientCommandFilter
from commands.server import ServerCommand

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
#   Helpers
from .helpers import _is_dead
#   Paths
from .paths import ES_EVENTS_PATH


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
    current_event_vars['es_{}deaths'.format(type_str)] = _is_dead(player)
    current_event_vars['es_{}kills'.format(type_str)] = player.kills
    current_event_vars['es_{}dead'.format(type_str)] = player.dead
    current_event_vars['es_{}index'.format(type_str)] = player.index

@PreHook(memory.get_virtual_function(game_event_manager, 'FireEvent'))
def pre_fire_event(args):
    event = memory.make_object(GameEvent, args[1])
    if noisy_cvar.get_int() != 1 and event.name in NOISY_EVENTS:
        return

    current_event_vars.clear()
    current_event_vars.update(event.variables.as_dict())

    userid = current_event_vars.get('userid', 0)
    if userid:
        fill_event_vars(userid, 'user')

    attacker = current_event_vars.get('attacker', 0)
    if attacker:
        fill_event_vars(attacker, 'attacker')

    import es
    es.addons.triggerEvent(event.name)


# =============================================================================
# >> CURRENT MAP & AUTO REFRESH PUBLIC CVARS
# =============================================================================
@OnLevelInit
def on_level_init(map_name):
    currentmap_cvar.set_string(map_name)

    if autorefreshvars_cvar.get_int() > 0:
        import es
        es.refreshpublicvars()

currentmap_cvar.set_string(global_vars.map_name)


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
    # TODO: Fire es_player_chat
    # TODO: es.regsaycmd() should be handled here and not with SP's
    #       get_say_command()
    userid = userid_from_index(index)
    if es.addons.sayFilter(userid, command.arg_string, team_only):
        return CommandReturn.CONTINUE

    return CommandReturn.BLOCK


# =============================================================================
# >> CLIENT COMMAND FILTER & es_client_command
# =============================================================================
@ClientCommandFilter
def on_client_command(command, index):
    import es
    userid = userid_from_index(index)
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
    engine_server.server_command('changelevel {}'.format(new_map))
    es.dbgmsg(0, '[EventScripts] Next map changed from {} to {}.'.format(
        command[1], new_map))
    return CommandReturn.BLOCK


# =============================================================================
# >> POST INITIALIZATION
# =============================================================================
def post_initialization():
    check_ip_cmdline()