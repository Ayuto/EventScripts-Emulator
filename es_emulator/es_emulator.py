# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import sys

# Source.Python
from cvars import cvar

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

    # TODO: There is a conflict between ES' and SP's keyvalues module
    #import _libs.python.keyvalues as x
    #sys.modules['keyvalues'] = x
    #es.load('esc')
    #es.load('corelib')

    print('ES Emulator has been loaded successfully!')

def unload():
    print('Unloading ES Emulator...')

    # TODO: Unload all ES addons

    print('Removing "{}" from sys.path.'.format(str(ES_PATH)))
    sys.path.remove(str(ES_PATH))

    print('Removing "{}" from sys.path.'.format(str(ES_LIBS_PATH)))
    sys.path.remove(str(ES_LIBS_PATH))

    # TODO:
    # 1. Delete console variables
    # 2. Delete console commands

    print('ES Emulator has been unloaded successfully!')