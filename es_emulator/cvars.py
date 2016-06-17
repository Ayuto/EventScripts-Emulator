# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from cvars import ConVar
from core import GAME_PATH

# ES Emulator
from .paths import ES_PATH


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
botcexec_cvar = ConVar(
    'eventscripts_bot-cexec',
    '0',
    'If set to 1, es_cexec* commands attempt to apply to bots. If set to 0, es_cexec* commands do not work on bots (old style)'
)

addondir_cvar = ConVar(
    'eventscripts_addondir',
    str(ES_PATH),
    'Full path to EventScripts addon directory (read-only)'
)

gamedir_cvar = ConVar(
    'eventscripts_gamedir',
    str(GAME_PATH)[:-1],
    'Full path to the Source mod you\'re playing.'
)