# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
#   Commands
from commands.typed import TypedServerCommand
from commands.server import ServerCommand
#   Engines
from engines.server import engine_server
#   Events
from events.manager import game_event_manager

# ES Emulator
#   Logic
from .logic import cfg_scripts
#   Cvars
from .cvars import scriptdir_cvar
#   Helpers
from .helpers import _print_all_registered_cfg_scripts


# =============================================================================
# >> CONSTANTS
# =============================================================================
PLUGIN_VERSION_DESCRIPTION = 'Mattie\'s EventScripts, http://www.eventscripts.com, Version:2.1.1.379'


# =============================================================================
# >> ES CONSOLE COMMANDS
# =============================================================================
# TODO:
# Description: prints the version of Mattie's EventScripts plugin
@ServerCommand('eventscripts_version')
def eventscripts_version(command):
    import es
    es.dbgmsg(0, PLUGIN_VERSION_DESCRIPTION)

# TODO:
# Description: logs the version of Mattie's EventScripts plugin
@ServerCommand('eventscripts_log')
def eventscripts_log(command):
    engine_server.log_print(PLUGIN_VERSION_DESCRIPTION)
    engine_server.log_print('\n')


# =============================================================================
# >> COMMANDS FOR OLD ES CFG SCRIPTS
# =============================================================================
# TODO:
# Description: Syntax : eventscripts_register [subdirectory]\n  Registers a script pack subdirectory or, with no parameters, lists all registered script packs.
@ServerCommand('eventscripts_register')
def eventscripts_register(command):
    if len(command) < 2:
        _print_all_registered_cfg_scripts()
        return

    import es

    scriptpack = command[1]
    cfg_scripts[scriptpack] = 1
    es.setinfo('{}_dir'.format(scriptpack), '"{}/{}/"'.format(
        scriptdir_cvar.get_string(), scriptpack))

    es.dbgmsg(0, '[EventScripts] Registered script pack: {}'.format(command.arg_string))

    event = game_event_manager.create_event('es_scriptpack_register', True)
    event.set_string('scriptpack', scriptpack)
    game_event_manager.fire_event(event)

# TODO:
# Description: Syntax : eventscripts_unregister [subdirectory]\n  Unregisters/disables a script pack subdirectory, or, with no parameters, lists all registered script packs.
@ServerCommand('eventscripts_unregister')
def eventscripts_unregister(command):
    if len(command) < 2:
        _print_all_registered_cfg_scripts()
        return

    import es
    scriptpack = command[1]

    event = game_event_manager.create_event('es_scriptpack_unregister', True)
    event.set_string('scriptpack', scriptpack)
    game_event_manager.fire_event(event)

    cfg_scripts[scriptpack] = 0
    es.dbgmsg(0, '[EventScripts] Unregistered script pack: {}'.format(
        command.arg_string))


# =============================================================================
# >> UNUSED INTERNAL ES COMMANDS
# =============================================================================
unused_internal_commands = (
    'es__clientcmdproxy',
    'es__cmdproxy',
    'es__createentity',
    'es__createentity2',
    'es__db',
    'es__de',
    'es__disable',
    'es__dispatcheffect',
    'es__eb',
    'es__entblock',
    'es__entsetname',
    'es__ep',
    'es__fire',
    'es__foreachkey',
    'es__foreachval',
    'es__give',
    'es__ip',
    'es__prop_dynamic_create',
    'es__prop_physics_create',
    'es__pyevent',
    'es__remove',
    'es__sb',
    'es__setang',
    'es__setpos',
    'es__unload',
    'es_x_disable',
    'es_x_foreachkey',
    'es_x_foreachval',
    'es_x_unload',
    '_mexecl',
    
    # TODO: cbench just needs to print a few lines
    'cbench',
    
    # TODO: Implement this. Add an extra config file to avoid a security risk?
    'pycmd_register'
)

for command in unused_internal_commands:
    ServerCommand(command, 'Internal ES Command')(lambda x: None)