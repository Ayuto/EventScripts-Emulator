# Copyright 2010, EventScripts Development Team
# ./addons/eventscripts/corelib/es_mexec/es_mexec.py
import es
import cmdlib
import time

import hashlib
from path import path

def memoryExecuteCommand(pathToConfigFile):
    """
    This function copies a configuration file from outside the ../cfg/ file to
    the ../cfg/ file to be executed by Valve's exec command. The reason why we
    need to copy the file is to ensure backwards compatibility as es_(x)mexec
    used to allow functionality of having configuration files outside of the
    ../cfg/ directory. Since the Valve console broke this functionality in the
    OB update, we need to simulate the functionality by copying the directory
    to a temporary unique file in the ../cfg/ directory.
    """
    pathToConfigFile = pathToConfigFile.strip('"')
    if not pathToConfigFile.startswith('..'):
        es.server.cmd('exec "%s"' % pathToConfigFile)
        return

    cfgFolder = path(str(es.ServerVar('eventscripts_gamedir'))).joinpath('cfg')
    individualCFGFile = cfgFolder.joinpath(pathToConfigFile)

    uniqueString = hashlib.md5(str(time.time())).hexdigest()
    configName = '%s.%s.mexec.cfg' % (individualCFGFile.namebase, uniqueString)
    newFile = cfgFolder.joinpath(configName)

    try:
        individualCFGFile.copyfile(newFile)
        es.server.cmd('exec "%s"' % configName)
        newFile.remove()
    except IOError:
        es.dbgmsg(0, "ERROR: es_mexec cannot find the file path %s" % pathToConfigFile)
         
es.mexec = memoryExecuteCommand


def mexec(args):
    if len(args):
        memoryExecuteCommand(str(args))
    else:
        es.dbgmsg(0, 'Syntax: es_mexec <"path">')

cmdlib.registerServerCommand('es_xmexec', mexec, 'Syntax: es_xmexec <"path">', skipcheck=True)


def expand(args):
    es.server.cmd('es es_xmexec ' + str(args))

cmdlib.registerServerCommand('es_mexec', expand, 'Syntax: es_mexec <"path">', skipcheck=True)