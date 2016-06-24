# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
#   Commands
from commands.typed import TypedServerCommand
from commands.server import ServerCommand
#   Engines
from engines.server import engine_server


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
def on_eventscripts_version(command):
    import es
    es.dbgmsg(0, PLUGIN_VERSION_DESCRIPTION)

# TODO:
# Description: logs the version of Mattie's EventScripts plugin
@ServerCommand('eventscripts_log')
def on_eventscripts_log(command):
    engine_server.log_print(PLUGIN_VERSION_DESCRIPTION)
    engine_server.log_print('\n')


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
)

for command in unused_internal_commands:
    ServerCommand(command, 'Internal ES Command')(lambda x: None)