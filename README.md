# EventScripts-Emulator
A Source.Python plugin that is able to run EventScripts addons.

This is just a fun project and I have actually sworn to not create something like this. However, I got bored the other day and was curious how difficult it will be to create it. The first test addons are already working!

# Development status
1. Most of EventScripts' es_C module functions have been roughly implemented.
2. At the moment I'm only focused on getting the Python side fully working. Later I hope to get the experimental shell engine working.

# Usage
1. Put ``es_emulator`` in ``../addons/source-python/plugins/``
2. Load the EventScripts Emulator with ``sp load es_emulator``
3. Put the EventScripts addon you would like to run in ``../addons/source-python/plugins/es_emulator/libs/``.
4. Load the addon via ``es_load <your addon>``.

Funny side note: You can also use the EventScripts API in Source.Python plugins.

# Note
I took the original EventScripts libraries from http://forums.eventscripts.com/index.php and adapted them to work with Python 3. I have also removed the test addons to keep it simple.
