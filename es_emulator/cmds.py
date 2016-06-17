# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from commands.typed import TypedServerCommand


# =============================================================================
# >> ES CONSOLE COMMANDS
# =============================================================================
@TypedServerCommand('es_load')
def es_load(command_info, addon=None):
    import es
    es.load(addon)

@TypedServerCommand('es_unload')
def es_unload(command_info, addon):
    import es
    es.unload(addon)

@TypedServerCommand('es_reload')
def es_reload(command_info, addon):
    import es
    es.reload(addon)