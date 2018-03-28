# EventScripts-Emulator
A [Source.Python](http://forums.sourcepython.com/) plugin that is able to run [EventScripts](http://forums.eventscripts.com/index.php) addons.

# Development status
Most of the work is already done. The following is a list of things that need to be done.

## General
1. Add the possibility to unload the emulator.
2. Do extensive testings

## Python
1. Implement es.forcevalue() - Revisit CS:GO implementation
2. Implement es.old_mexec()
3. Implement es.physics('start', ...)
4. Implement es.regexec()
5. Implement es.keyprecursivekeycopy()
6. es.createentitylist() - Add full server class dump

## ESS
1. Implement pycmd_register

## Console variables
1. Implement mattie_eventscripts
2. Implement eventscripts_debug_showfunctions
3. Implement mattie_python

# Usage
1. Put ``es_emulator`` in ``../addons/source-python/plugins/``
2. Load the EventScripts Emulator with ``sp plugin load es_emulator``
3. Put the EventScripts addon you would like to run in ``../addons/source-python/plugins/es_emulator/eventscripts/``.
4. Run the server command ``ese convert <your addon name>`` to run the Python 2 to 3 converter.
5. Load the addon via ``es_load <your addon>``.

Funny side note: You can also use the EventScripts API in Source.Python plugins.

# Differences

* es.getuserid() also works with SteamID3. A possible crash has also been fixed when using handles.

# Note
I took the original EventScripts libraries from the latest release and adapted them to work with Python 3. I have also removed the example addons like ``mugmod`` or ``slingshot`` to keep it simple.

Unlike EventScripts this emulator also supports CS:GO. Though, es.usermsg()/es_usermsg is not supported. Use the usermsg library directly.
