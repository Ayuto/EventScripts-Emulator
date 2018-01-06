# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
from path import Path

# Source.Python
from core import PLATFORM
from paths import GAME_PATH


# =============================================================================
# >> CONSTANTS
# =============================================================================
PLUGIN_PATH = Path(__file__).parent
ES_PATH = PLUGIN_PATH / 'eventscripts'
ES_LIBS_PATH = ES_PATH / '_libs' / 'python'
DATA_PATH = PLUGIN_PATH / 'data'
ES_EVENTS_PATH = DATA_PATH / 'mattie_eventscripts.res'
POPUPLIB_POPUP_RES_PATH = ES_PATH / 'popup' / 'popup.res'

if PLATFORM == 'windows':
    PLAT_EXT = '.dll'
else:
    PLAT_EXT = '.so'

BIN_PATH = GAME_PATH / 'bin'

def get_server_binary():
    binary = BIN_PATH / 'server{}'.format(PLAT_EXT)
    if not binary.isfile():
        binary = BIN_PATH / 'server_srv{}'.format(PLAT_EXT)

        if not binary.isfile():
            raise NameError('Unable to find server binary.')

    return binary

SERVER_BINARY = get_server_binary()