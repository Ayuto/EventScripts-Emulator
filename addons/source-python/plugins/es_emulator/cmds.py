# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import lib2to3.main

# Source.Python
#   Commands
from commands.typed import TypedServerCommand
from commands.server import ServerCommand
from commands.typed import ValidationError
#   Cvars
from cvars import cvar
#   Engines
from engines.server import engine_server
#   Entities
from entities.entity import BaseEntity
#   Events
from events.manager import game_event_manager

# ES Emulator
from .paths import ES_PATH
#   Logic
from .logic import cfg_scripts
#   Cvars
from .cvars import scriptdir_cvar
#   Helpers
from .helpers import _print_all_registered_cfg_scripts
from .helpers import Error


# =============================================================================
# >> CONSTANTS
# =============================================================================
PLUGIN_VERSION_DESCRIPTION = 'Mattie\'s EventScripts, http://www.eventscripts.com, Version:2.1.1.379'


# =============================================================================
# >> ES EMULATOR COMMANDS
# =============================================================================
@TypedServerCommand(['ese', 'convert'])
def _convert_addon(info, addon, backup:bool=True):
    """Convert an addon from Python 2 to Python 3."""
    args = ['-w']
    if not backup:
        args.append('-n')

    addon_path = ES_PATH / addon
    if not addon_path.is_dir():
        raise ValidationError('Addon "{}" does not exist.'.format(addon))

    args.append(str(addon_path))

    lib2to3.main.main('lib2to3.fixes', args)


# =============================================================================
# >> ES CONSOLE COMMANDS
# =============================================================================
@ServerCommand('eventscripts_version', 'prints the version of Mattie\'s EventScripts plugin')
def eventscripts_version(command):
    import es
    es.dbgmsg(0, PLUGIN_VERSION_DESCRIPTION)

@ServerCommand('eventscripts_log', 'logs the version of Mattie\'s EventScripts plugin')
def eventscripts_log(command):
    engine_server.log_print(PLUGIN_VERSION_DESCRIPTION)
    engine_server.log_print('\n')


# =============================================================================
# >> COMMANDS FOR OLD ES CFG SCRIPTS
# =============================================================================
@ServerCommand('eventscripts_register', 'Syntax : eventscripts_register [subdirectory]\n  Registers a script pack subdirectory or, with no parameters, lists all registered script packs.')
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

@ServerCommand('eventscripts_unregister', 'Syntax : eventscripts_unregister [subdirectory]\n  Unregisters/disables a script pack subdirectory, or, with no parameters, lists all registered script packs.')
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

@ServerCommand('cbench', 'Do some benchmarks for C++')
def cbench(command):
    import es
    es.dbgmsg(0, 'starting benchmarks for C++...')
    es.dbgmsg(0, 'format() benchmark: 0.062670 seconds')
    es.dbgmsg(0, 'str benchmark: 0.000138 seconds')
    es.dbgmsg(0, 'replace benchmark: 0.002908 seconds')
    es.dbgmsg(0, 'int benchmark: 0.000061 seconds')
    es.dbgmsg(0, 'float benchmark: 0.000101 seconds')


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

    # TODO: Implement this. Add an extra config file to avoid a security risk?
    'pycmd_register'
)

for command in unused_internal_commands:
    ServerCommand(command, 'Internal ES Command')(lambda x: None)


# =============================================================================
# >> COMPATIBILITY COMMAND FOR CS:GO (used by es_trick)
# =============================================================================
def Test_CreateEntity(command):
    if len(command) < 2:
        Error('Test_CreateEntity: requires entity classname argument.')

    try:
        BaseEntity.create(command[1])
    except:
        Error(f'Test_CreateEntity( {command[1]} ) failed.')


if cvar.find_command('Test_CreateEntity') is None:
    ServerCommand('Test_CreateEntity')(Test_CreateEntity)
