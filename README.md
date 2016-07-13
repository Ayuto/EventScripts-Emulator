# EventScripts-Emulator
A [Source.Python](http://forums.sourcepython.com/) plugin that is able to run [EventScripts](http://forums.eventscripts.com/index.php) addons.

This is just a fun project and I have actually sworn to not create something like this. However, I got bored the other day and was curious how difficult it will be to create it. The first test addons are already working!

# Development status
1. Almost all ESP functions and ESS commands have been implemented.
2. Logic for Python, Shell and config based addons has been implemented.
3. Logic for almost all console variables has been implemented.

If I would need to guess, I would say 80-90% of the project is implemented.

# TODO:
1. Implement the last few Python functions.
2. Implement the last few Shell commands.
3. Add the possibility to unload the emulator.
4. Do extensive testings.

# Usage
1. Put ``es_emulator`` in ``../addons/source-python/plugins/``
2. Load the EventScripts Emulator with ``sp load es_emulator``
3. Put the EventScripts addon you would like to run in ``../addons/source-python/plugins/es_emulator/libs/``.
4. Load the addon via ``es_load <your addon>``.

Funny side note: You can also use the EventScripts API in Source.Python plugins.

# Note
I took the original EventScripts libraries from the latest release and adapted them to work with Python 3. I have also removed the example addons like ``mugmod`` or ``slingshot`` to keep it simple.
