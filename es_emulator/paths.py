# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
from path import Path


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
PLUGIN_PATH = Path(__file__).parent
ES_PATH = PLUGIN_PATH / 'libs'
ES_LIBS_PATH = ES_PATH / '_libs' / 'python'
DATA_PATH = PLUGIN_PATH / 'data'
ES_EVENTS_PATH = DATA_PATH / 'mattie_eventscripts.res'