# ./addons/eventscripts/corelib/average/average.py
# ported to Python by Hunter
# original command by cagemonkey

import es
import cmdlib

def load():
    cmdlib.registerServerCommand('average', average_cmd, 'Averages numbers and can round the output. Syntax: average <var> [type] 1 2 3 etc')

    for line in (
        'testcase qcreate corelib averagetest "Tests average"',
        'testcase addtest averagetest averagetest corelib/average/testcase "Average Corelib Command Test"'):
        es.server.queuecmd(line)

def unload():
    cmdlib.unregisterServerCommand('average')

def average_cmd(args):
    numbers = []
    if len(args) > 2 and args[1].startswith('#'):
        for index in range(2, len(args)):
            numbers.append(float(args[index]))
    elif len(args) > 1 and not args[1].startswith('#'):
        for index in range(1, len(args)):
            numbers.append(float(args[index]))
    if numbers:
        result = sum(numbers)/len(numbers)
        if args[1] == '#round':
            es.ServerVar(args[0]).set(int(round(result)))
        elif args[1] == '#ceiling':
            es.ServerVar(args[0]).set(int(result)+1)
        elif args[1] == '#floor':
            es.ServerVar(args[0]).set(int(result))
        else:
            es.ServerVar(args[0]).set(float(result))
    else:
        es.dbgmsg(0, 'average: Not enough arguments to average. Syntax: average <var> [type] <number> <number> <etc>')

def testcase():
    for line in (
        'profile begin average_test',
        'profile begin average_normal',
        'testlib begin average_normal "average 3 3 6 3"',
        'es_xset _average_testvar 0',
        'average _average_testvar 3 3 6 3',
        'testlib fail_unless _average_testvar equalto 3.750000',
        'testlib end',
        'profile end average_normal',
        'profile begin average_round',
        'testlib begin average_round "average #round 3 3 6 3"',
        'es_xset _average_testvar 0',
        'average _average_testvar #round 3 3 6 3',
        'testlib fail_unless _average_testvar equalto 4',
        'testlib end',
        'profile end average_round',
        'profile begin average_ceiling',
        'testlib begin average_ceiling "average #ceiling 3 3 6 3"',
        'es_xset _average_testvar 0',
        'average _average_testvar #ceiling 3 3 6 3',
        'testlib fail_unless _average_testvar equalto 4',
        'testlib end',
        'profile end average_ceiling',
        'profile begin average_floor',
        'testlib begin average_floor "average #floor 3 3 6 3"',
        'es_xset _average_testvar 0',
        'average _average_testvar #floor 3 3 6 3',
        'testlib fail_unless _average_testvar equalto 3',
        'testlib end',
        'profile end average_floor',
        'profile end average_test'):
        es.server.cmd(line)
