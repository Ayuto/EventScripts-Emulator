# ./addons/eventscripts/corelib/timelib/timelib.py
# ported to Python by Hunter
# original command by MyFly

import es
import cmdlib

import time

def load():
    cmdlib.registerServerCommand('gettime', gettime_cmd, 'Syntax: gettime <variable> <format>')

    for line in (
        'testcase qcreate corelib timelibtest "Tests timelib"',
        'testcase addtest timelibtest timelibtest corelib/timelib/testcase "Timelib Corelib Command Test"'):
        es.server.queuecmd(line)

def unload():
    cmdlib.unregisterServerCommand('gettime')

def gettime_cmd(args):
    if len(args) > 1:
        es.ServerVar(args[0]).set(str(time.strftime(args[1])))
    else:
        es.dbgmsg(0, 'gettime: Not enough arguments to gettime. Syntax: gettime <variable> <format>')

def testcase():
    for line in (
        'profile begin timelib_test',
        'testlib begin timelib_test "gettime test"',
        'es_xset _timelib_testvar 0',
        'es_xset _timelib_original 0',
        'es_xset _timelib_format 0',
        'es_xcopy _timelib_format eventscripts_timeformat',
        'es_xset eventscripts_timeformat "%m-%d-%Y_%H:%M:%S"',
        'es_xgettimestring _timelib_original',
        'es_xcopy eventscripts_timeformat _timelib_format',
        'gettime _timelib_testvar "%m-%d-%Y_%H:%M:%S"',
        'es testlib fail_unless _timelib_testvar equalto server_var(_timelib_original)',
        'testlib end',
        'profile end timelib_test'):
        es.server.cmd(line)
