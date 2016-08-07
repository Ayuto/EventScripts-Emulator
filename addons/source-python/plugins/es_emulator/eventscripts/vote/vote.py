# ./addons/eventscripts/vote/vote.py
# ported to Python by Hunter

#vote create <name> <callback-blockname> [vote-callback-blockname]
#vote delete <name>
#vote exists <var> <name>
#vote isrunning <var> <name>
#vote setquestion <name> '<question>'
#vote setanswer <name> <option#> '<answer>'
#vote addanswer <name> '<answer>'
#vote remanswer <name> <option#>
#vote start <name> [time]
#vote stop <name> [cancel]
#vote send <name> <userid> [force]
#vote submit <name> <userid> <option#> [force]
#vote getvotes <var> <name> [answer]
#vote gettimeleft <var> <name>
#vote showmenu <name> <0/1>
#vote endtime <name> <0/1>
#vote enduser <name> <0/1>
#vote setvar <name> <variable> <value>
#vote getvar <name> <var> <variable>
#vote list

import es
import cmdlib

import playerlib
import votelib

def load():
    cmdlib.registerServerCommand('vote', vote_cmd, 'Vote console command')

def unload():
    cmdlib.unregisterServerCommand('vote')

def vote_cmd(args):
    if len(args):
        subcmd = args[0].lower()
        if len(args) > 1:
            vname = args[1]
        else:
            vname = ''
        if len(vname) and votelib.exists(vname):
            v = votelib.find(vname)
        else:
            v = None
        if subcmd == 'create':
            if vname:
                if len(args) > 2:
                    endblock = args[2]
                else:
                    endblock = None
                if len(args) > 3:
                    subblock = args[3]
                else:
                    subblock = None
                votelib.create(vname, endblock, subblock)
            else:
                es.dbgmsg(0, 'Syntax: vote create <name> <end-callback> [submit-callback]')
        elif subcmd == 'delete':
            if vname:
                if v:
                    votelib.delete(vname)
                else:
                    es.dbgmsg(0, 'vote delete: No such vote: %s' % vname)
            else:
                es.dbgmsg(0, 'Syntax: vote delete <name>')
        elif subcmd == 'exists':
            if len(args) > 2:
                es.ServerVar(args[1]).set(int(votelib.exists(args[2])))
            else:
                es.dbgmsg(0, 'Syntax: vote exists <var> <name>')
        elif subcmd == 'isrunning':
            if len(args) > 2:
                es.ServerVar(args[1]).set(int(votelib.isrunning(args[2])))
            else:
                es.dbgmsg(0, 'Syntax: vote isrunning <var> <name>')
        elif subcmd == 'getvotes':
            if len(args) > 2:
                es.ServerVar(args[1]).set(int(votelib.isrunning(args[2])))
            else:
                es.dbgmsg(0, 'Syntax: vote isrunning <var> <name>')
        elif subcmd == 'getvotes':
            if len(args) > 2:
                if votelib.exists(args[2]):
                    if len(args) > 3 and args[3].isdigit():
                        es.ServerVar(args[1]).set(int(votelib.find(args[2]).getvotes(args[3])))
                    else:
                        es.ServerVar(args[1]).set(int(votelib.find(args[2]).getvotes()))
                else:
                    es.dbgmsg(0, 'vote getvotes: No such vote: %s' % vname)
            else:
                es.dbgmsg(0, 'Syntax: vote getvotes <var> <name> [option#]')
        elif subcmd == 'gettimeleft':
            if len(args) > 2:
                if votelib.exists(args[2]):
                    es.ServerVar(args[1]).set(int(votelib.find(args[2]).gettimeleft()))
                else:
                    es.dbgmsg(0, 'vote getvotes: No such vote: %s' % vname)
            else:
                es.dbgmsg(0, 'Syntax: vote gettimeleft <var> <name>')
        elif subcmd == 'setquestion':
            if len(args) > 2:
                if v:
                    v.setquestion(args[2])
                else:
                    es.dbgmsg(0, 'vote setquestion: No such vote: %s' % vname)
            else:
                es.dbgmsg(0, 'Syntax: vote setoption <name> <option#> "<answer>"')
        elif subcmd == 'setoption' or subcmd == 'setanswer':
            if len(args) > 3:
                if v:
                    v.setoption(int(args[2]), args[3])
                else:
                    es.dbgmsg(0, 'vote setoption: No such vote: %s' % vname)
            else:
                es.dbgmsg(0, 'Syntax: vote setoption <name> <option#> "<answer>"')
        elif subcmd == 'addoption' or subcmd == 'addanswer':
            if len(args) > 2:
                if v:
                    v.addoption(args[2])
                else:
                    es.dbgmsg(0, 'vote addoption: No such vote: %s' % vname)
            else:
                es.dbgmsg(0, 'Syntax: vote addoption <name> "<answer>"')
        elif subcmd == 'deloption' or subcmd == 'remanswer':
            if len(args) > 2:
                if v:
                    v.deloption(int(args[2]))
                else:
                    es.dbgmsg(0, 'vote deloption: No such vote: %s' % vname)
            else:
                es.dbgmsg(0, 'Syntax: vote deloption <name> <option#>')
        elif subcmd == 'start':
            if len(args) > 1:
                if v:
                    if len(args) > 2:
                        v.start(int(args[2]))
                    else:
                        v.start(0)
                else:
                    es.dbgmsg(0, 'vote start: No such vote: %s' % vname)
            else:
                es.dbgmsg(0, 'Syntax: vote start <name> [time]')
        elif subcmd == 'stop':
            if len(args) > 1:
                if v:
                    v.stop(len(args) > 2 and str(args[2]) == '1')
                else:
                    es.dbgmsg(0, 'vote stop: No such vote: %s' % vname)
            else:
                es.dbgmsg(0, 'Syntax: vote stop <name> [cancel]')
        elif subcmd == 'send':
            if len(args) > 2:
                if v:
                    if '#' in args[2]:
                        args[2] = args[2].replace('#', ',#')[1:]
                    v.send(playerlib.getUseridList(args[2]), len(args) > 3 and str(args[3]) == '1')
                else:
                    es.dbgmsg(0, 'vote send: No such vote: %s' % vname)
            else:
                es.dbgmsg(0, 'Syntax: vote send <name> <users> [force]')
        elif subcmd == 'submit':
            if len(args) > 3:
                if v:
                    if '#' in args[2]:
                        args[2] = args[2].replace('#', ',#')[1:]
                    v.submit(playerlib.getUseridList(args[2]), int(args[3]), len(args) > 4 and str(args[4]) == '1')
                else:
                    es.dbgmsg(0, 'vote submit: No such vote: %s' % vname)
            else:
                es.dbgmsg(0, 'Syntax: vote submit <name> <users> <option#> [force]')
        elif subcmd == 'showmenu':
            if len(args) > 2:
                if v:
                    v.showmenu = str(args[2]) == '1'
                else:
                    es.dbgmsg(0, 'vote showmenu: No such vote: %s' % vname)
            else:
                es.dbgmsg(0, 'Syntax: vote showmenu <name> <0/1>')
        elif subcmd == 'endtime':
            if len(args) > 2:
                if v:
                    v.endtime = str(args[2]) == '1'
                else:
                    es.dbgmsg(0, 'vote endtime: No such vote: %s' % vname)
            else:
                es.dbgmsg(0, 'Syntax: vote endtime <name> <0/1>')
        elif subcmd == 'enduser':
            if len(args) > 2:
                if v:
                    v.enduser = str(args[2]) == '1'
                else:
                    es.dbgmsg(0, 'vote enduser: No such vote: %s' % vname)
            else:
                es.dbgmsg(0, 'Syntax: vote enduser <name> <0/1>')
        elif subcmd == 'setvar':
            if len(args) > 3:
                if v:
                    if args[2].isalnum():
                        setattr(v, args[2], args[3])
                    else:
                        es.dbgmsg(0, 'vote setvar: Invalid vote variable name')
                else:
                    es.dbgmsg(0, 'vote setvar: No such vote: %s' % kname)
            else:
                es.dbgmsg(0, 'Syntax: vote setvar <name> <variable> <value>')
        elif subcmd == 'getvar':
            if len(args) > 4:
                if v:
                    if args[3].isalnum() and hasattr(v, args[3]):
                        es.ServerVar(args[2]).set(getattr(v, args[3]))
                    else:
                        es.dbgmsg(0, 'vote getvar: Invalid vote variable name')
                else:
                    es.dbgmsg(0, 'vote getvar: No such vote: %s' % kname)
            else:
                es.dbgmsg(0, 'Syntax: vote getvar <name> <var> <variable>')
        elif subcmd == 'list':
            if len(args) > 1:
                listlevel = int(vname)
            else:
                listlevel = 0
            for vname in votelib.getvotelist():
                votelib.find(vname).information(listlevel)
            if not len(args) > 1:
                es.dbgmsg(0, ' ')
                es.dbgmsg(0, 'For more details, supply list level (0-2):')
                es.dbgmsg(0, 'Syntax: vote list [level]')
        elif subcmd == 'info':
            if v:
                v.information(listlevel, 2)
            else:
                es.dbgmsg(0, 'vote info: No such vote: %s' % kname)
            if not len(args) > 1:
                es.dbgmsg(0, ' ')
                es.dbgmsg(0, 'Syntax: vote info <name>')
        else:
            es.dbgmsg(0, 'Invalid vote subcommand, see http://www.eventscripts.com/pages/Vote/ for a list of subcommands')
    else:
        es.dbgmsg(0, 'Missing vote subcommand, see http://www.eventscripts.com/pages/Vote/ for a list of subcommands')
