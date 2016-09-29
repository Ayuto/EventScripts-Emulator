# EventScripts-Emulator
A [Source.Python](http://forums.sourcepython.com/) plugin that is able to run [EventScripts](http://forums.eventscripts.com/index.php) addons.

This is just a fun project and I have actually sworn to not create something like this. However, I got bored the other day and was curious how difficult it will be to create it. The first test addons are already working!

# Development status
## General
1. Add the possibility to unload the emulator.
2. Do extensive testings

## Python
1. Implemented es.dosql()
2. Implement es.forcevalue()
3. Implement es.mathparse()
4. Implement es.old_mexec()
5. Implement es.physics('start', ...)
6. Implement es.regexec()
7. Implement es.sql()
8. Implement es.keyprecursivekeycopy()
9. es.dumpserverclasses() - Retrieve m_InstanceBaselineIndex
10. es.getuserid() - Fix for SteamID3 or leave it like the original one?
11. es.createentitylist() - Add full server class dump
12. es.createplayerlist() - Add packetloss and ping
13. es.dbgmsg() - Create a proper implementation

## ESS
1. es_dumpusermessages - Print size of user message
2. Implement cbench
3. Implement pycmd_register
4. Add description to eventscripts_version
5. Add description to eventscripts_log
6. Add description to eventscripts_register
7. Add description to eventscripts_unregister

## Console variables
1. Implement mattie_eventscripts
2. Implement eventscripts_debug
3. Implement eventscripts_debug_showfunctions
4. Implement eventscripts_debuglog
5. Implement eventscripts_servergamedll_ver
6. Implement eventscripts_servergameclients_ver
7. Implement eventscripts_quote
8. Implement mattie_python

# Usage
1. Put ``es_emulator`` in ``../addons/source-python/plugins/``
2. Load the EventScripts Emulator with ``sp load es_emulator``
3. Put the EventScripts addon you would like to run in ``../addons/source-python/plugins/es_emulator/libs/``.
4. Load the addon via ``es_load <your addon>``.

Funny side note: You can also use the EventScripts API in Source.Python plugins.

# Note
I took the original EventScripts libraries from the latest release and adapted them to work with Python 3. I have also removed the example addons like ``mugmod`` or ``slingshot`` to keep it simple.
