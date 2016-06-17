# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
#   Memory
import memory

from memory.hooks import PreHook
#   Events
from events import GameEvent
from events.manager import game_event_manager
#   Engines
from engines.server import global_vars
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

# EventScripts Emulator
#   Cvars
from .cvars import noisy_cvar
from .cvars import currentmap_cvar
from .cvars import autorefreshvars_cvar
#   Helpers
from .helpers import _is_dead


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
# >> LISTENERS
# =============================================================================
@OnTick
def on_tick():
    import es
    es.addons.tick()

@SayFilter
def on_say(command, index, team_only):
    import es
    # TODO: Fire es_player_chat
    userid = userid_from_index(index)
    if es.addons.sayFilter(userid, command.arg_string, team_only):
        return CommandReturn.CONTINUE

    return CommandReturn.BLOCK

@ClientCommandFilter
def on_client_command(command, index):
    import es
    userid = userid_from_index(index)
    if es.addons.clientCommand(userid):
        return CommandReturn.CONTINUE

    return CommandReturn.BLOCK