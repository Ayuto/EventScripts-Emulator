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
#@TypedServerCommand('es_load')
def es_load(command_info, addon=None):
    import es
    es.load(addon)

#@TypedServerCommand('es_unload')
def es_unload(command_info, addon):
    import es
    es.unload(addon)

#@TypedServerCommand('es_reload')
def es_reload(command_info, addon):
    import es
    es.reload(addon)

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