# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import sys
import muparser

# Source.Python
from cvars import cvar
from cvars import ConVar

# ES Emulator
from .paths import ES_PATH
from .paths import ES_LIBS_PATH


# =============================================================================
# >> NOTES
# =============================================================================
# 1.
# Never import the "es" module or any of the other modules via libs.<module>.
# It will cause the module to be imported twice.


# =============================================================================
# >> LOAD & UNLOAD
# =============================================================================
def load():
    print('Loading ES Emulator...')

    if cvar.find_var('eventscripts_addondir') is not None:
        raise ValueError('EventScripts is already loaded.')

    print('Adding "{}" to sys.path.'.format(str(ES_PATH)))
    sys.path.append(str(ES_PATH))

    print('Adding "{}" to sys.path.'.format(ES_LIBS_PATH))
    sys.path.append(str(ES_LIBS_PATH))

    print('Initializing console variables...')
    from . import cvars

    print('Initializing console commands...')
    from . import cmds

    print('Initializing logic...')
    from . import logic

    print('Initializing EventScripts...')
    import es

    logic.post_initialization()

    # TODO: There is a conflict between ES' and SP's keyvalues module
    import _libs.python.keyvalues as x
    sys.modules['keyvalues'] = x
    es.load('esc')
    es.server.queuecmd('es_load corelib')

    print('ES Emulator has been loaded successfully!')

def unload():
    print('Unloading ES Emulator...')

    # TODO: Unload all ES addons

    print('Removing "{}" from sys.path.'.format(str(ES_PATH)))
    sys.path.remove(str(ES_PATH))

    print('Removing "{}" from sys.path.'.format(str(ES_LIBS_PATH)))
    sys.path.remove(str(ES_LIBS_PATH))

    print('Removing console variables...')
    from . import cvars
    for name in dir(cvars):
        obj = getattr(cvars, name)
        if isinstance(obj, ConVar):
            cvar.unregister_base(obj)

    # 2. Delete console commands

    print('Unloading MuParser...')
    muparser.unload_parser()

    print('ES Emulator has been unloaded successfully!')
