import es
import playerlib
import settinglib

#plugin information
info = es.AddonInfo()
info.name = "Setting EventScripts python library"
info.version = "oy1"
info.author = "Hunter"
info.url = "http://www.eventscripts.com/pages/Setting/"
info.description = "Provides user based setting handling for Source games"
info.basename = "setting"


###########################################
#EventScripts events and blocks start here#
###########################################

def load():
    if not es.exists("command", "setting"):
        es.regcmd("setting", "setting/consolecmd", "Setting console command")

#setting create <settingname> "<description>" [type]
#setting delete <settingname>
#setting clear <settingname> [time-difference]
#setting exists <return-var> <settingname>
#setting settitle <settingname> "<description>"
#setting addoption <settingname> <option-key> <option-name> "[description]"
#setting remoption <settingname> <option-key>
#setting clearoption <settingname>
#setting addsound <settingname> <sound-path>
#setting remsound <settingname>
#setting send <settingname> <userid> [locked]
#setting sendglobal <settingname> <userid> [locked]
#setting getvar <return-var> <settingname> <variable-name> [userid]
#setting setvar <settingname> <variable-name> <value> [userid]
#setting resend <settingname> <1/0>
#setting backmenu <settingname> <keymenu/popup>
#setting list

# For "list" settings:
#setting setdefault <settingname> <option-key> [overwrite]
#setting get <return-var> <settingname> [userid]
#setting set <settingname> <option-key> [userid]

# For "toggle" settings:
#setting setdefault <settingname> <option-key> <1/0> [overwrite]
#setting get <return-var> <settingname> <option-key> [userid]
#setting set <settingname> <option-key> <1/0> [userid]
#setting toggle <settingname> <option-key> [userid]

def consolecmd():
    #Command from server console or non-python script
    subcmd = es.getargv(1).lower()
    sname = es.getargv(2)
    argc = es.getargc()
    if sname in settinglib.gSettings:
        s = settinglib.gSettings[sname]
    else:
        s = None
    if subcmd == "create":
        if sname:
            descr = es.getargv(3)
            stype = es.getargv(4)
            if stype == "0": stype = None
            settinglib.create(sname,descr,stype)
        else:
            es.dbgmsg(0,"Syntax: setting create <settingname> \"<description>\" [type]")
    elif subcmd == "delete":
        if sname:
            if s:
                settinglib.delete(sname)
            else:
                es.dbgmsg(0,"Setting delete: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax: setting delete <settingname>")
    elif subcmd == "exists":
        if argc == 4:
            retvar = es.getargv(2)
            sname = es.getargv(3)
            es.set(retvar,int(settinglib.exists(sname)))
        else:
            es.dbgmsg(0,"Syntax: setting exists <var> <settingname>")
    elif subcmd == "clear":
        if sname:
            if s:
                time = es.getargv(3)
                if time == "0": time = None
                s.clear(time)
            else:
                es.dbgmsg(0,"Setting clear: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax: setting clear <settingname>")
    elif subcmd == "getsettings":
        if argc == 4:
            retvar = es.getargv(2)
            sname = es.getargv(3)
            if argc == 5:
                option = int(es.getargv(4))
            else:
                option = None
            es.set(retvar,int(settinglib.getsettings(sname,option)))
        else:
            es.dbgmsg(0,"Syntax: setting getsettings <var> <settingname> [option#]")
    elif subcmd == "gettimeleft":
        if argc == 4:
            retvar = es.getargv(2)
            sname = es.getargv(3)
            es.set(retvar,int(settinglib.gettimeleft(sname)))
        else:
            es.dbgmsg(0,"Syntax: setting gettimeleft <var> <settingname>")
    elif (subcmd == "setdescription") or (subcmd == "settitle"):
        if argc == 4:
            if s:
                descr = str(es.getargv(3))
                s.setdescription(descr)
            else:
                es.dbgmsg(0,"Setting setdescription: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax: setting setdescription <settingname> \"<description>\"")
    elif subcmd == "setoption":
        if argc >= 5:
            if s:
                option = es.getargv(3)
                text = str(es.getargv(4))
                if es.getargv(5):
                    state = bool(int(es.getargv(5)))
                else:
                    state = False
                s.setoption(option,text,state)
            else:
                es.dbgmsg(0,"Setting setoption: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax: setting setoption <settingname> <option-key> <option-name> [1/0]")
    elif subcmd == "addoption":
        if argc >= 5:
            if s:
                option = es.getargv(3)
                text = str(es.getargv(4))
                if es.getargv(5):
                    state = bool(int(es.getargv(5)))
                else:
                    state = False
                s.addoption(option,text,state)
            else:
                es.dbgmsg(0,"Setting addoption: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax: setting addoption <settingname> <option-key> <option-name> [1/0]")
    elif (subcmd == "deloption") or (subcmd == "remoption"):
        if argc == 4:
            if s:
                option = es.getargv(3)
                s.deloption(option)
            else:
                es.dbgmsg(0,"Setting deloption: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax: setting deloption <settingname> <option-key>")
    elif subcmd == "clearoption":
        if sname:
            if s:
                s.clearoption()
            else:
                es.dbgmsg(0,"Setting clearoption: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax: setting clearoption <settingname>")
    elif subcmd == "addsound":
        if argc == 4:
            if s:
                sound = es.getargv(3)
                s.addsound(sound)
            else:
                es.dbgmsg(0,"Setting addsound: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax: setting addsound <settingname> <sound-path>")
    elif (subcmd == "delsound") or (subcmd == "remsound"):
        if sname:
            if s:
                s.delsound()
            else:
                es.dbgmsg(0,"Setting delsound: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax: setting delsound <settingname>")
    elif subcmd == "send":
        if argc >= 4:
            if s:
                users = es.getargv(3)
                if es.getargv(4):
                    locked = bool(int(es.getargv(4)))
                else:
                    locked = False
                s.send(playerlib.getUseridList(users),False,locked)
            else:
                es.dbgmsg(0,"Setting send: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax: setting send <settingname> <users> [locked]")
    elif subcmd == "sendglobal":
        if argc >= 4:
            if s:
                users = es.getargv(3)
                if es.getargv(4):
                    locked = bool(int(es.getargv(4)))
                else:
                    locked = False
                s.sendglobal(playerlib.getUseridList(users),False,locked)
            else:
                es.dbgmsg(0,"Setting send: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax: setting send <settingname> <users> [locked]")
    elif subcmd == "resend":
        if argc == 4:
            if s:
                try:
                    s.resend = bool(int(es.getargv(3)))
                except ValueError:
                    s.resend = False
            else:
                es.dbgmsg(0,"Setting resend: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax: setting resend <settingname> <0/1>")
    elif subcmd == "backmenu":
        if argc == 4:
            if s:
                s.backmenu(es.getargv(3))
            else:
                es.dbgmsg(0,"No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax: setting backmenu <settingname> <keymenu/popup>")
    elif subcmd == "setvar":
        if argc >= 5:
            if s:
                varp = es.getargv(3)
                varv = es.getargv(4)
                if es.getargv(5):
                    userid = int(es.getargv(5))
                else:
                    userid = None
                if varp.isalnum():
                    s.setvar(varp, varv)
                else:
                    es.dbgmsg(0,"Invalid setting variable name")
            else:
                es.dbgmsg(0,"Setting setvar: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax: setting setvar <settingname> <variable> <value> [userid]")
    elif subcmd == "getvar":
        if argc >= 5:
            sname = es.getargv(3)
            if sname in settinglib.gSettings:
                s = settinglib.gSettings[sname]
            else:
                s = None
            if s:
                varp = es.getargv(2)
                varv = es.getargv(4)
                if es.getargv(5):
                    userid = int(es.getargv(5))
                else:
                    userid = None
                if varv.isalnum():
                    es.set(varp, s.getvar(varv, userid))
                else:
                    es.dbgmsg(0,"Invalid setting variable name")
            else:
                es.dbgmsg(0,"Setting getvar: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax: setting getvar <var> <settingname> <variable> [userid]")
    elif subcmd == "setdefault":
        if argc >= 4:
            if s:
                if s.keyvalues["config"]["type"] == "list":
                    option = es.getargv(3)
                    if es.getargv(4):
                        overwrite = bool(int(es.getargv(4)))
                    else:
                        overwrite = False
                    s.setdefault(option,overwrite)
                elif s.keyvalues["config"]["type"] == "toggle":
                    option = es.getargv(3)
                    state = bool(int(es.getargv(4)))
                    if es.getargv(5):
                        overwrite = bool(int(es.getargv(5)))
                    else:
                        overwrite = False
                    s.setdefault(option,state,overwrite)
            else:
                es.dbgmsg(0,"Setting setdefault: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax list: setting setdefault <settingname> <option-key> [overwrite]")
            es.dbgmsg(0,"Syntax toggle: setting setdefault <settingname> <option-key> <1/0> [overwrite]")
    elif subcmd == "get":
        if argc >= 4:
            retvar = es.getargv(2)
            sname = es.getargv(3)
            if sname in settinglib.gSettings:
                s = settinglib.gSettings[sname]
            else:
                s = None
            if s:
                if s.keyvalues["config"]["type"] == "list":
                    if es.getargv(4):
                        userid = int(es.getargv(4))
                    else:
                        userid = None
                    es.set(retvar,s.get(userid))
                elif s.keyvalues["config"]["type"] == "toggle":
                    option = es.getargv(4)
                    if es.getargv(5):
                        userid = int(es.getargv(5))
                    else:
                        userid = None
                    es.set(retvar,s.get(option,userid))
            else:
                es.dbgmsg(0,"Setting get: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax list: setting get <return-var> <settingname> [userid]")
            es.dbgmsg(0,"Syntax toggle: setting get <return-var> <settingname> <option-key> [userid]")
    elif subcmd == "set":
        if argc >= 4:
            if s:
                if s.keyvalues["config"]["type"] == "list":
                    option = es.getargv(3)
                    if es.getargv(4):
                        userid = int(es.getargv(4))
                    else:
                        userid = None
                    s.set(option,userid)
                elif s.keyvalues["config"]["type"] == "toggle":
                    option = es.getargv(3)
                    state = bool(int(es.getargv(4)))
                    if es.getargv(5):
                        userid = int(es.getargv(5))
                    else:
                        userid = None
                    s.set(option,state,userid)
            else:
                es.dbgmsg(0,"Setting set: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax list: setting set <settingname> <option-key> [userid]")
            es.dbgmsg(0,"Syntax toggle: setting set <settingname> <option-key> <1/0> [userid]")
    elif subcmd == "toggle":
        if argc >= 4:
            if s:
                if s.keyvalues["config"]["type"] == "toggle":
                    option = es.getargv(3)
                    if es.getargv(4):
                        userid = int(es.getargv(4))
                    else:
                        userid = None
                    s.toggle(option,userid)
                else:
                    es.dbgmsg(0,"Setting toggle: No toggle-type setting: "+sname)
            else:
                es.dbgmsg(0,"Setting toggle: No such setting: "+sname)
        else:
            es.dbgmsg(0,"Syntax: setting toggle <settingname> <option-key> [userid]")
    elif subcmd == "save":
        settinglib._saveAll()
    elif subcmd == "list":
        es.dbgmsg(0,"---------- List of settings:")
        if argc == 2:
            listlevel = 0
        else:
            listlevel = int(sname)
        for sname in settinglib.gSettings:
            s = settinglib.gSettings[sname]
            s.information(listlevel)
        if argc == 2:
            es.dbgmsg(0, " ")
            es.dbgmsg(0, "For more details, supply list level (0-2):")
            es.dbgmsg(0, "Syntax: setting list [level]")
        es.dbgmsg(0,"----------")
    elif subcmd == "info":
        if argc >= 3:
            if argc == 4:
                listlevel = int(es.getargv(3))
            else:
                listlevel = 2
            if v:
                s.information(listlevel)
        else:
            es.dbgmsg(0, "Syntax: setting info <settingname> [level]")
    else:
        es.dbgmsg(0,"Invalid setting subcommand, see http://www.eventscripts.com/pages/Setting/ for help")
