# ./addons/eventscripts/corelib/isnumerical/isnumerical.py
# ported to Python by Hunter
# original command by Chun

import es
import cmdlib

def load():
    cmdlib.registerServerCommand('isnumerical', isnumerical_cmd, 'Stores whether or not a string is numerical in a var. Syntax: isnumerical <variable> <string>')

    for line in (
        'testcase qcreate corelib isnumericaltest "Tests isnumerical"',
        'testcase addtest isnumericaltest isnumericaltest corelib/isnumerical/testcase "Isnumerical Corelib Command Test"'):
        es.server.queuecmd(line)

def unload():
    cmdlib.unregisterServerCommand('isnumerical')

def isnumerical_cmd(args):
    if len(args) > 1:
        try:
            value = float(args[1])
            value = True
        except:
            value = False
        if value:
            es.ServerVar(args[0]).set(1)
        else:
            es.ServerVar(args[0]).set(0)
    else:
        es.dbgmsg(0, 'isnumerical: Not enough arguments to isnumerical. Syntax: isnumerical <variable> <string>')

def testcase():
    for line in (
        'profile begin isnumerical_test',
        'testlib begin isn1 "isnumerical test 1 - numerical string"',
        'es_xset _isn_testvar 0',
        'isnumerical _isn_testvar 32367',
        'testlib fail_unless _isn_testvar equalto 1',
        'testlib end',
        'testlib begin isn2 "isnumerical test 2 - non-numerical string"',
        'es_xset _isn_testvar 0',
        'isnumerical _isn_testvar wsae3425',
        'testlib fail_unless _isn_testvar equalto 0',
        'testlib end',
        'testlib begin isn3 "isnumerical test 3 - negative numerical string"',
        'es_xset _isn_testvar 0',
        'isnumerical _isn_testvar -3478',
        'testlib fail_unless _isn_testvar equalto 1',
        'testlib end',
        'testlib begin isn4 "isnumerical test 4 - decimal string"',
        'es_xset _isn_testvar 0',
        'isnumerical _isn_testvar 323.67',
        'testlib fail_unless _isn_testvar equalto 1',
        'testlib end',
        'testlib begin isn1 "isnumerical test 5 - negative decimal string"',
        'es_xset _isn_testvar 0',
        'isnumerical _isn_testvar -23434.1256',
        'testlib fail_unless _isn_testvar equalto 1',
        'testlib end',
        'profile end isnumerical_test'):
        es.server.cmd(line)
