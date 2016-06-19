# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import sys

# Source.Python
#   Core
from core import GAME_PATH
#   Cvars
from cvars import ConVar
from cvars.flags import ConVarFlags

# ES Emulator
from .paths import ES_PATH


# =============================================================================
# >> NOT IMPLEMENTED CVARS
# =============================================================================
eventscripts_cvar = ConVar(
    'mattie_eventscripts',
    '1',
    'Turns on scripts that run on every server event.',
    ConVarFlags.REPLICATED | ConVarFlags.NOTIFY
)

debug_cvar = ConVar(
    'eventscripts_debug',
    '0',
    'Turns on debug print output for EventScripts. Use only if you want to debug problems.'
)

debugfunctions_cvar = ConVar(
    'eventscripts_debug_showfunctions',
    '0',
    'Adds internal ES function names and line numbers to debug strings for parsing.'
)

debuglog_cvar = ConVar(
    'eventscripts_debuglog',
    '0',
    'Will send debug messages to server log as well as console if this is set to 1.'
)

scriptdir_cvar = ConVar(
    'eventscripts_subdirectory',
    '',
    'Specifies an alternate directory for configuration files. Must be a subdirectory of your cfg directory.'
)

datadir_cvar = ConVar(
    'eventscripts_datadirectory',
    'cfg',
    'Specifies an alternate directory for output files.'
)

escape_cvar = ConVar(
    'eventscripts_escapechars',
    '; {}()\':',
    'Lists the characters for that cause variable expansion to require quotes to prevent parsing issues. (Leave this alone unless you know what you\'re doing.)'
)

timeformat_cvar = ConVar(
    'eventscripts_timeformat',
    '%Y-%m-%d %H:%M:%S (%Z)',
    'Format for time strings retrieved by es_gettimestring.'
)

execmd_cvar = ConVar(
    'eventscripts_exec-cmd',
    'exec',
    'The name of the \'exec\' command that EventScripts uses internally.'
)

serverdll_cvar = ConVar(
    'eventscripts_servergamedll_ver',
    '',
    'Version of ServerGameDLL used by EventScripts. (read only)'
)

serverclients_cvar = ConVar(
    'eventscripts_servergameclients_ver',
    '',
    'Version of ServerGameClients interface used by EventScripts. (read only)'
)

quote_cvar = ConVar(
    'eventscripts_quote',
    '"',
    'A quotation mark. A tool, not a variable.'
)

python_cvar = ConVar(
    'mattie_python',
    '1',
    'Enable Python support for EventScripts'
)


# =============================================================================
# >> IMPLEMENTED CVARS
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

noisy_cvar = ConVar(
    'eventscripts_noisy',
    '0',
    'Turns on script handling for noisy GameEvents (footsteps, reloads, etc).'
)

currentmap_cvar = ConVar(
    'eventscripts_currentmap',
    '',
    'Current map.'
)

lang_cvar = ConVar(
    'eventscripts_language',
    'english',
    'Name of the default language for EventScripts scripts to use. Supports the same values as cl_language for clients.'
)

autorefreshvars_cvar = ConVar(
    'eventscripts_autorefreshvars',
    '1',
    'If set to 1, EventScripts will try to refresh global change callbacks for every public cvar on each new map.'
)

deadflag_cvar = ConVar(
    'eventscripts_deadflag',
    '1',
    'If set to 1, uses fast but less stable method of detecting player\'s dead state. If set to 0, reverts to using Valve\'s method (delayed).'
)

protectrcon_cvar = ConVar(
    'eventscripts_protectrcon',
    '1',
    'Add FCVAR_PROTECTED flag to rcon_password so that it will resolve properly.'
)

sayevents_cvar = ConVar(
    'eventscripts_chatevent',
    '1',
    'If set to 1, EventScripts will trigger the es_player_chat event, otherwise it will not.'
)

nextmap_cvar = ConVar(
    'eventscripts_nextmapoverride',
    '',
    'Set this to a map name that will override the next changelevel command to use this map.'
)

mapcommands_cvar = ConVar(
    'eventscripts_maphandler',
    '1',
    'If set to 1, EventScripts will allow level change replacement. Must be set in autoexec.cfg or on command-line.'
)

cmdline_cvar = ConVar(
    'eventscripts_cmdline',
    ' '.join(sys.argv),
    'Server\'s command-line information.'
)

setipcmdline_cvar = ConVar(
    'eventscripts_setipcmdline',
    '1',
    'EventScripts will set the IP for you passed from a +ip command-line.'
)

lastgive_cvar = ConVar(
    'eventscripts_lastgive',
    '',
    'Last given entity index'
)

frametimer_cvar = ConVar(
    'eventscripts_frametimecheck',
    '0',
    'If set to 1, EventScripts will output timing warnings when a GameFrame takes longer than 0.01 seconds inside scripts.'
)

cmdprefix_cvar = ConVar(
    'eventscripts_cmdprefixes',
    '!',
    'A list of single character prefixes which will be passed to es_client_command.cfg when fired.'
)

scripttrace_cvar = ConVar(
    'eventscripts_scripttrace',
    '0',
    'Turns on script tracing.'
)

autocreate_cvar = ConVar(
    'eventscripts_autocreate',
    '0',
    'Automatically create new console variables when EventScripts commands are used on nonexistent variables.'
)


# =============================================================================
# >> UNUSED CVARS
# =============================================================================
interface_cvar = ConVar(
    'eventscripts_eiface',
    '1',
    'Internal function for helping EventScripts choose the right ImmediateExecuteCommand for command ordering.'
)

cflags_cvar = ConVar(
    'eventscripts_cflags',
    '902',
    'Obsolete. eventscripts_cflags'
)

maxmessages_cvar = ConVar(
    'eventscripts_maxmsg',
    '28',
    'Maximum number of usermessages supported by the mod. Do not change unless instructed to do so.'
)

defaultevents_cvar = ConVar(
    'eventscripts_defaultevents',
    '1',
    'If set to 1, EventScripts will try to register for the default event files on each new map.'
)

shellengine_cvar = ConVar(
    'eventscripts_shellengine',
    '1',
    'Turns on Python-based ESC script engine'
)
