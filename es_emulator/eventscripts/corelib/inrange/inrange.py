# ./addons/eventscripts/corelib/inrange/inrange.py
# ported to Python by Hunter
# original command by cagemonkey

import es
import cmdlib

def load():
    cmdlib.registerServerCommand('inrange', inrange_cmd, 'Syntax: inrange <var> <value1> <range> <value2>')

    for line in (
        'testcase qcreate corelib inrangetest "Tests inrange"',
        'testcase addtest inrangetest inrangetest corelib/inrange/testcase "Inrange Corelib Command Test"'):
        es.server.queuecmd(line)

def unload():
    cmdlib.unregisterServerCommand('inrange')

def inrange_cmd(args):
    if len(args) > 3:
        es.ServerVar(args[0]).set(int(abs(float(args[1]) - float(args[3])) <= float(args[2])))
    else:
        es.dbgmsg(0, 'inrange: Not enough arguments to inrange. Syntax: inrange <var> <value1> <range> <value2>')

def testcase():
    for line in (
        'profile begin inrange_test',
        'testlib begin inrange_true "inrange 10 7 15"',
        'es_xset _inrange_testvar 0',
        'inrange _inrange_testvar 10 7 15',
        'testlib fail_unless _inrange_testvar equalto 1',
        'testlib end',
        'profile end inrange_true',
        'profile begin inrange_false',
        'testlib begin inrange_false "inrange 10 3 15"',
        'es_xset _inrange_testvar 0',
        'inrange _inrange_testvar 10 3 15',
        'testlib fail_unless _inrange_testvar equalto 0',
        'testlib end',
        'profile end inrange_false',
        'profile end inrange_test'):
        es.server.cmd(line)
