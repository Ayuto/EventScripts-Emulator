import es
import playerlib
import popuplib

#plugin information
info = es.AddonInfo()
info.name = "Popup library wrapper"
info.version = "oy29"
info.author = "GODJonez + ES 2.0 Beta Test team"
info.url = "http://www.eventscripts.com/pages/Popup/"
info.description = "Provides menu and pop-up handling for Source games"
info.basename = "popup"


###########################################
#EventScripts events and blocks start here#
###########################################

def load():
    if not es.exists("command", "popup"):
        es.regcmd("popup", "popup/consolecmd", "Popup console command")

def consolecmd():
    #Command from server console or non-python script
    subcmd = es.getargv(1).lower()
    pname = es.getargv(2)
    argc = es.getargc()
    if pname in popuplib.gPopups:
        p = popuplib.gPopups[pname]
    else:
        p = None
    debug = info
    if subcmd == "create":
        if pname:
            popuplib.create(pname)
        else:
            es.dbgmsg(0,"Syntax: popup create <popupname>")
    elif subcmd == "delete":
        if pname:
            if p:
                popuplib.delete(pname)
            else:
                es.dbgmsg(0,"Popup delete: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup delete <popupname>")
    elif subcmd == "addline":
        if argc == 4:
            if p:
                text = str(es.getargv(3))
                p.addline(text)
            else:
                es.dbgmsg(0,"Popup addline: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup addline <popupname> <text>")
    elif subcmd == "delline":
        if argc == 4:
            if p:
                line = int(es.getargv(3))
                p.delline(line)
            else:
                es.dbgmsg(0,"Popup delline: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup delline <popupname> <line#>")
    elif subcmd == "insline":
        if argc == 5:
            if p:
                line = int(es.getargv(3))
                text = str(es.getargv(4))
                p.insline(line, text)
            else:
                es.dbgmsg(0,"Popup insline: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup insline <popupname> <line#> <text>")
    elif subcmd == "modline":
        if argc == 5:
            if p:
                line = int(es.getargv(3))
                text = str(es.getargv(4))
                p.modline(line, text)
            else:
                es.dbgmsg(0,"Popup modline: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup modline <popupname> <line#> <text>")
    elif subcmd == "prepuser":
        if argc == 4:
            if p:
                block = str(es.getargv(3))
                if block == "0": block = ""
                p.prepuser = block
            else:
                es.dbgmsg(0,"Popup prepuser: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup prepuser <popupname> <block>")
    elif subcmd == "menuselect":
        if argc == 4:
            if p:
                block = es.getargv(3)
                if block == "0": block = ""
                p.menuselect = block
            else:
                es.dbgmsg(0,"Popup menuselect: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup menuselect <popupname> <block>")
    elif subcmd == "menuselectfb":
        if argc == 4:
            if p:
                block = es.getargv(3)
                if block == "0": block = ""
                p.menuselectfb = block
            else:
                es.dbgmsg(0,"Popup menuselectfb: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup menuselectfb <popupname> <block>")
    elif subcmd == "select":
        if argc == 5:
            if p:
                item = int(es.getargv(3))
                block = es.getargv(4)
                if block == "0": block = ""
                p.select(item, block)
            else:
                es.dbgmsg(0,"Popup select: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup select <popupname> <choice#> <block>")
    elif subcmd == "submenu":
        if argc == 5:
            if p:
                item = int(es.getargv(3))
                block = es.getargv(4)
                if block == "0": block = ""
                p.submenu(item, block)
            else:
                es.dbgmsg(0,"Popup submenu: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup submenu <popupname> <choice#> <submenu>")
    elif subcmd == "menuvalue":
        if argc == 6:
            if p:
                item = int(es.getargv(4))
                varn = es.getargv(3)
                varv = es.getargv(5)
                p.menuvalue(varn, item, varv)
            else:
                es.dbgmsg(0,"Popup menuvalue: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup menuvalue <popupname> <variable> <choice#> <value>")
    elif subcmd == "timeout":
        if argc == 5:
            if p:
                tomode = es.getargv(3)
                time = float(es.getargv(4))
                p.timeout(tomode, time)
            else:
                es.dbgmsg(0,"Popup timeout: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup timeout <popupname> <mode> <time>")
            es.dbgmsg(0," mode: \"send\" or \"view\"")
    elif subcmd == "send":
        if argc == 5:
            try:
                prio = bool(int(es.getargv(4)))
            except ValueError:
                prio = False
        else:
            prio = False
        if argc >= 4:
            if p:
                users = es.getargv(3)
                p.send(playerlib.getUseridList(users),prio)
            else:
                es.dbgmsg(0,"Popup send:No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup send <popupname> <users>")
    elif subcmd == "unsendname":
        if argc == 4:
            if p:
                users = es.getargv(3)
                popuplib.unsendname(pname, playerlib.getUseridList(users))
            else:
                es.dbgmsg(0,"Popup unsendname: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup unsendname <popupname> <users>")
    elif subcmd == "close":
        if argc == 4:
            if p:
                users = es.getargv(3)
                popuplib.close(pname, playerlib.getUseridList(users))
            else:
                es.dbgmsg(0,"Popup close: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup close <popupname> <users>")
    elif subcmd == "isqueued":
        if argc == 5:
            if p:
                retvar = es.getargv(3)
                userid = int(es.getargv(4))
                es.set(retvar,popuplib.isqueued(pname,userid))
            else:
                es.dbgmsg(0,"Popup isqueued: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup isqueued <popupname> <var> <userid>")
    elif subcmd == "active":
        if argc == 5:
            retvar = es.getargv(3)
            userid = int(es.getargv(4))
            try:
                r = popuplib.active(userid)
                es.set(pname,r['name'])
                es.set(retvar,r['count'])
            except KeyError:
                es.dbgmsg(0,"Popup active: No userid "+str(userid)+" on server.")
        else:
            es.dbgmsg(0,"Syntax: popup active <name var> <count var> <userid>")
    elif subcmd == "exists":
        if argc == 4:
            retvar = es.getargv(3)
            es.set(retvar,int(popuplib.exists(pname)))
        else:
            es.dbgmsg(0,"Syntax: popup exists <popupname> <var>")
    elif subcmd == "addlinef":
        if argc > 3:
            if p:
                text = _formatv(3)
                p.addline(text)
            else:
                es.dbgmsg(0,"Popup addlinef: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup addlinef <popupname> <format> [vartoken1] ... [vartoken9]")
    elif subcmd == "inslinef":
        if argc > 4:
            if p:
                line = int(es.getargv(3))
                text = _formatv(4)
                p.insline(line,text)
            else:
                es.dbgmsg(0,"Popup inslinef: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup inslinef <popupname> <line#> <format> [vartoken1] ... [vartoken9]")
    elif subcmd == "modlinef":
        if argc > 4:
            if p:
                line = int(es.getargv(3))
                text = _formatv(4)
                p.modline(line,text)
            else:
                es.dbgmsg(0,"Popup modlinef: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup modlinef <popupname> <line#> <format> [vartoken1] ... [vartoken9]")
    elif subcmd == "cachemode":
        if argc == 4:
            if p:
                tomode = es.getargv(3)
                p.cachemode = tomode
            else:
                es.dbgmsg(0,"Popup cachemode: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup cachemode <popupname> <mode>")
            es.dbgmsg(0," mode: \"global\", \"static\" or \"user\"")
    elif subcmd == "recache":
        if argc > 2:
            if p:
                if argc == 4:
                    users = playerlib.getUseridList(es.getargv(3))
                    p.recache(users)
                else: p.recache()
            else:
                es.dbgmsg(0,"Popup recache: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup recache <popupname> [users]")
    elif subcmd == "update":
        if argc == 4:
            if p:
                users = playerlib.getUseridList(es.getargv(3))
                p.update(users)
            else:
                es.dbgmsg(0,"Popup update: No such popup: "+pname)
        else:
            es.dbgsmg(0,"Syntax: popup update <popupname> <users>")
    elif subcmd == "displaymode":
        if argc == 4:
            if p:
                tomode = es.getargv(3)
                p.displaymode = tomode
            else:
                es.dbgmsg(0,"Popup displaymode: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup displaymode <popupname> <mode>")
            es.dbgmsg(0," mode: \"normal\" or \"sticky\"")
    elif subcmd == "construct":
        if argc == 6:
            varp = es.getargv(5)
        else:
            varp = "_popup_choice"
        if argc >= 5:
            plist = es.getargv(3)
            pflags = es.getargv(4)
            nep = popuplib.construct(pname,plist,pflags)
            nep.c_savevar = varp
        else:
            es.dbgmsg(0,"Syntax: popup construct <popupname> <list> <flags> [var]")
    elif subcmd == "setvar":
        if argc == 5:
            if p:
                ok = False
                varp = es.getargv(3)
                if varp.isalnum():
                    ok = True
                else:
                    if varp[:2] == "c_" and varp[2:].isalnum():
                        ok = True
                varv = es.getargv(4)
                if ok:
                    p.__setattr__(varp,varv)
                else:
                    es.dbgmsg(0,"Invalid popup variable name")
            else:
                es.dbgmsg(0,"Popup setvar: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup setvar <popupname> <variable> <value>")
    elif subcmd == "getvar":
        if argc == 5:
            if p:
                ok = False
                varp = es.getargv(3)
                varv = es.getargv(4)
                if varv.isalnum():
                    ok = True
                else:
                    if varv[:2] == "c_" and varv[2:].isalnum():
                        ok = True
                if ok:
                    es.set(varp, p.__getattr__(varv))
                else:
                    es.dbgmsg(0,"Invalid popup variable name")
            else:
                es.dbgmsg(0,"Popup getvar: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup getvar <popupname> <var> <variable>")
    elif subcmd == "easymenu":
        if argc == 5:
            varp = es.getargv(3)
            block = es.getargv(4)
            popuplib.easymenu(pname,varp,block)
        else:
            es.dbgmsg(0,"Syntax: popup easymenu <popupname> <var> <block>")
    elif subcmd == "addoption":
        if argc > 4:
            if p:
                item = str(es.getargv(3))
                text = str(es.getargv(4))
                if argc == 6: state = int(es.getargv(5))
                else: state = 1
                p.addoption(item, text, state)
            else:
                es.dbgmsg(0,"Easymenu addoption: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup addoption <popupname> <value> <text> [state]")
    elif subcmd == "setoption":
        if argc > 3:
            if p:
                item = int(es.getargv(3))
                if argc == 5:
                    text = es.getargv(4)
                    if int(text) > 0 and int(text) <= 2 or str(text) == '0':
                        p.setoption(item,None,int(text))
                    else:
                        p.setoption(item,text,None)
                elif argc == 6:
                    text = es.getargv(4)
                    state = int(es.getargv(5))
                    p.setoption(item,text,state)
            else:
                es.dbgmsg(0,"Easymenu setoption: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup setoption <popupname> <item> [text] [state]")
    elif subcmd == "description":
        if argc == 4:
            if p:
                text = es.getargv(3)
                p.setdescription(text)
            else:
                es.dbgmsg(0,"Popup description: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Usage: popup description <popupname> <text>")
    elif subcmd == "info":
        if argc >= 3:
            if argc == 4:
                listlevel = int(es.getargv(3))
            else:
                listlevel = 4
            if p:
                p.information(listlevel)
        else:
            es.dbgmsg(0, "Syntax: popup info <popupname> [level]")
    elif subcmd == "emulate":
        if argc == 5:
            if p:
                item = int(es.getargv(3))
                users = es.getargv(4)
                popuplib.emulate(pname,item,users)
            else:
                es.dbgmsg(0,"Popup emulate: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup emulate <popupname> <choice#> <users>")
    elif subcmd == "editlang":
        if argc == 4:
            if p:
                p.editlang = str(es.getargv(3))
            else:
                es.dbgmsg(0,"Popup editlang: No such popup: "+pname)
        else:
            es.dbgmsg(0,"Syntax: popup editlang <popupname> <language>")
    elif subcmd == "setstyle":
        if argc >= 3:
            style = es.getargv(argc-1)
            passvalue = 0
            if style.startswith("radio"): passvalue |= 1
            if style.startswith("esc"): passvalue |= 2
            if style.endswith("!"): passvalue |= 128
            if argc == 4:
                if p:
                    p.visualstyle = passvalue
                else:
                    es.dbgmsg(0,"Popup setstyle: No such popup: "+pname)
            else:
                popuplib.gameSupportAdmin = passvalue
        else:
            es.dbgmsg(0,"Syntax: popup setstyle [popupname] {auto|radio|esc}[!]")
    elif subcmd == "quicksend":
        if argc == 6:
            block = str(es.getargv(5))
        else:
            block = ""
        if argc > 4:
            time = float(es.getargv(2))
            userid = float(es.getargv(3))
            text = str(es.getargv(4))
            popuplib.quicksend(time,userid,text,block)
        else:
            es.dbgmsg(0,"Syntax: popup quicksend <time> <userid> <text> [block]")
    elif subcmd == "list":
        es.dbgmsg(0,"---------- List of popups:")
        if argc == 2:
            listlevel = 0
        else:
            listlevel = int(pname)
        for pname in popuplib.gPopups:
            p = popuplib.gPopups[pname]
            p.information(listlevel)
        if argc == 2:
            es.dbgmsg(0, " ")
            es.dbgmsg(0, "For more details, supply list level (0-4):")
            es.dbgmsg(0, "Syntax: popup list [level]")
        es.dbgmsg(0,"----------")
    else:
        es.dbgmsg(0,"Invalid popup subcommand, see http://www.eventscripts.com/pages/Popup/ for help")

def _formatv(findex):
    count = es.getargc()
    format = es.getargv(findex)
    num = 0
    for indx in range(findex+1,count):
        num += 1
        format = format.replace("%"+str(num),str(es.server_var[es.getargv(indx)]))
    return format

