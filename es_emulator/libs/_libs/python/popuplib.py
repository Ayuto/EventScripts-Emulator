import es
import playerlib
import math
import gamethread
import msglib
import sys

import collections

#plugin information
info = es.AddonInfo()
info.name = "Popup EventScripts Python library"
info.version = "oy30m"
info.author = "GODJonez + EventScripts release team"
info.url = "http://python.eventscripts.com/pages/Popuplib"
info.description = "Provides menu and pop-up handling for Source games"

#global variables:
## gLanguage and gGamename are used by popup.construct and popup.easymenu
gLanguage = "en"
gGamename = "unknown"
# Game support information (game 'none' is my testing environment)
gameSupport = {
    'cstrike': (True, 4),
    'dod': (True, 4),
    'hl2mp': (False, 0),
    'tf': (True, 4),
    'synergy': (True, 4),
    'pvkii': (True, 4),
    'none': (True, 0),
    'unknown': (False, 0),
    }

#gameSupportAdmin is a value set by server administrator using popup setstyle command
# 0   = use autodetection
# 1   = force radio style popups
# 2   = force VGUI style popups
# 128 = do not allow popups to override
gameSupportAdmin = 0

## gPopups holds all the popups by their names for backwards compatibility
gPopups = {}

gConstructs = {}

# Static data to be displayed in popup generated content:
langdata = {}
langdata['en'] = {'prev': "Back", 'next': "Next", 'quit': "Cancel", 'pending': "Pending"}                               #by [NATO]Hunter
langdata['fr'] = {'prev': "Retour", 'next': "Suivant", 'quit': "Annuler", 'pending': "En attente"}                       #by Nicolous
langdata['de'] = {'prev': "Zur\xc3\xbcck", 'next': "Weiter", 'quit': 'Schlie\xc3\x9fen', 'pending': "Wechselnd"}       #by [NATO]Hunter
langdata['fi'] = {'prev': 'Edellinen', 'next': 'Seuraava', 'quit': 'Sulje', 'pending': 'Odottaa'}                       #by GODJonez
langdata['no'] = {'prev': 'Tilbake', 'next': 'Neste', 'quit': 'Avslutt', 'pending': 'I p\xc3\xa5vente av'}
teamdata = {}
teamdata['cstrike'] = {0: "UN", 1: "SPEC", 2: "T", 3: "CT"}
teamdata['dod'] = {0: "UN", 1: "SPEC", 2: "AL", 3: "AX"}
cbotdata = {0: "HUMAN", 1: "BOT"}
cdeaddata = {0: "", 1: "DEAD"}

# Get this library handle for registering events dynamically:
selfmodule = __import__(__name__)



class Popup_base(object):
    '''
    Popup_base class is the base of all popup types,
    do not use this class directly from anywhere except for
    checking variable type
    '''
    def __init__(self, pPopupid):
        '''
        Initialize the popup by creating necessary attributes
        '''
        self.name = pPopupid            #popup name for backwards compatibility
        self.vguititle = pPopupid       #display name for VGUI dialog captions
        self.timeoutsend = 0            #timeout in seconds for being in queue
        self.timeoutview = 0            #timeout for being visible
        self.prepuser = ""              #prepuser block
        self.oldskooltov = False        #old (ES 1.2 - ES 1.3) behavior on timeout view
        self.editlang = "default"       #Language to be edited
        self.displaymode = "normal"     #mode, "normal" or "sticky" (only applicable to normal popups)
        self.processing = False         #state data, is the popup being processed
        self.visualstyle = 0            #0 = autodetect, 1 = radio, 2 = VGUI
        self._cached_radio_menu = True  #magic value, was isRadioMenu True or False the last time
        self.enablekeys = ""            #numbers that trigger menuselect
    def isRadioMenu(self):
        '''
        Performs prioritized checking on whether the menu is to be displayed
        as radio menu or VGUI dialog
        '''
        isradio = gameSupport[gGamename][0]
        if gameSupportAdmin & 2:
            isradio = False
        if gameSupportAdmin & 1:
            isradio = True
        if gameSupportAdmin & 128:
            return isradio
        if self.visualstyle & 2:
            isradio = False
        if self.visualstyle & 1:
            isradio = True
        return isradio
    def i_userlang(self, userid):
        '''
        INTERNAL
        Returns a usable language code from cache,
        tries to conform to the language the user itself is using
        '''
        user = gUsers[int(userid)]
        if user:
            userlang = user.language
            if userlang not in self.cache:
                if gLanguage in self.cache:
                    return gLanguage
                else:
                    k = list(self.cache.keys())
                    if len(k) == 0:
                        return None
                    else:
                        return k[0]
            return userlang
        return None
    def i_endlang(self, userid):
        '''
        INTERNAL
        User wrapper for i_endlangg
        '''
        return self.i_endlangg(gUsers[int(userid)].language)
    def i_endlangg(self, userlang):
        '''
        INTERNAL
        Returns usable language code for constructable strings,
        tries to conform to the language passed in
        '''
        if userlang not in langdata:
            if gLanguage in langdata:
                return gLanguage
            else:
                k = list(langdata.keys())
                if len(k) == 0:
                    return None
                else:
                    return k[0]
        return userlang
    def delete(self):
        '''
        delete this popup, calls global delete function
        '''
        delete(self.name)
    def timeout(self, mode, time):
        '''
        set send/view timeout
        '''
        if (time >= 0):
            if (mode == "send"):
                self.timeoutsend = time
            elif (mode == "view"):
                self.timeoutview = time
            else:
                raise ValueError("Popuplib: Unsupported timeout mode: "+str(mode))
        else:
            raise ValueError("Popuplib: Invalid time value for timeout: "+str(time))
    def send(self, pUsers, prio=False):
        '''
        send this popup to users queue
        '''
        es.dbgmsg(1,"Popuplib: send %s to %s with prio=%s"%(self.name,str(pUsers),str(prio)))
        try:
            # try if pUsers is just a single userid
            userid = int(pUsers)
            pUsers = [userid]
        except TypeError:
            pass
        for userid in pUsers:
            #Priorization system:
            # if the user just used a chat or client command, he requested this popup to be sent
            # so send it immediately and put the older one to queue
            user = gUsers[int(userid)]
            if not user:
                continue
            es.dbgmsg(1,"Popuplib: send to "+str(userid)+" with prio="+str(prio))
            if self.isRadioMenu():
                es.dbgmsg(1,"Popuplib: user.prioritized="+str(user.prioritized))
                if not user.prioritized and _allow_event_info:
                    try:
                        es.dbgmsg(1,"Popuplib2: trying...")
                        testuserid = int(es.getEventInfo('userid'))
                        es.dbgmsg(1,"Popuplib2: testuserid=%d",testuserid)
                        if userid == testuserid:
                            es.dbgmsg(1,"Popuplib2: userid match")
                            cevent = str(es.getEventInfo('text'))
                            es.dbgmsg(1,'Popuplib2: cevent="%s"',cevent)
                            if cevent != "":
                                prio = True
                            if str(es.getEventInfo('es_event')) == "es_client_command":
                                prio = True
                    except(ValueError, TypeError):
                        pass
                    es.dbgmsg(1, 'Popuplib2: Done trying eventinfo')
                    try:
                        es.dbgmsg(1, 'Popuplib2: trying cmduserid...')
                        es.set('testuserid','0')
                        #es.server.cmd('es_xgetcmduserid testuserid')
                        #if userid == int(es.server_var['testuserid']):
                        #    prio = True
                        if userid == int(es.getcmduserid()):
                            prio = True
                    except TypeError:
                        pass
                    es.dbgmsg(1, 'Popuplib2: Done trying cmduserid')
                myqueuepos = 0
                if self.displaymode == "sticky":
                    myqueuepos = user.isqueued(self)
                es.dbgmsg(1,"Popuplib: myqueuepos = %d"%myqueuepos)
                if prio:
                    es.dbgmsg(1, 'Popuplib2: prio == True')
                    if user.active:
                        es.dbgmsg(1, 'Popuplib2: user.active != None')
                        user.queue[user.activeid] = user.active
                        if myqueuepos != 1:
                            if myqueuepos:
                                del user.queue[myqueuepos]
                            index = user.activeid - 1
                            user.queue[index] = self
                        user.active = None
                    else:
                        prio = False
                    user.prioritized = True
                    es.dbgmsg(1, 'Popuplib2: gamethread.queue')
                    gamethread.queue(gt_priofinish, user)
                if not prio:
                    es.dbgmsg(1, 'Popuplib2: prio == False')
                    if myqueuepos == 0:
                        index = user.nextindex
                        user.nextindex += 1
                        user.queue[index] = self
                if not user.closemode:
                    es.dbgmsg(1, 'Popuplib2: user.closemode == False')
                    # if in closemode, soon there will be menuselect 10!
                    es.dbgmsg(1, 'Popuplib2: user.handleQueue()')
                    user.handleQueue()
                else:
                    es.dbgmsg(1, 'Popuplib2: user.closemode == TRUE!')
                if self.timeoutsend > 0:
                    es.dbgmsg(1, 'Popuplib2: self.timeoutsend > 0, gamethread.delayed (%s, %s)'%(index,int(userid)))
                    gamethread.delayedname(self.timeoutsend, "_popup_"+self.name, unsend, (index, int(userid)))
            else:
                es.dbgmsg(1, 'Popuplib: Using VGUI dialog')
                if user.active:
                    user.queue[user.activeid] = self
                    user.active = None
                else:
                    user.queue[user.nextindex] = self
                user.handleQueue()
                
    def unsend(self, pUsers):
        '''
        remove this popup from users queue and display
        '''
        try:
            user = gUsers[int(pUsers)]
            if user: user.unsend(self, True)
        except TypeError:
            for userid in pUsers:
                user = gUsers[int(userid)]
                if user: user.unsend(self, True)
        
    def update(self, pUsers):
        '''
        redisplay this popup if its the visible one
        '''
        es.dbgmsg(1,"Popuplib: update("+str(pUsers)+str(type(pUsers))+")")
        try:
            user = gUsers[int(pUsers)]
            if user: user.updatePopup(self)
        except TypeError:
            for userid in pUsers:
                user = gUsers[int(userid)]
                if user: user.updatePopup(self)
    

class Popup_popup(Popup_base):
    '''
    Popup_popup is the normal popup class that inherits Popup_base
    by this it has automatically access to the methods and variables
    defined in Popup_base class
    '''
    def __init__(self, pPopupid):
        '''
        Initialize the popup by creating all necessary attributes
        with their default values
        '''
        # First call the Popup_base initialization:
        Popup_base.__init__(self, pPopupid)
        # Initialize variables
        self.lines = {}                 #contains the lines to be shown (inside languages)
        self.menuselect = ""            #menuselect block
        self.menuselectfb = ""          #menuselect fallback block
        self.p_select = {}              #dictionary of select blocks
        self.p_submenu = {}             #dictionary of submenu choices
        self.menuvar = {}               #menu variables
        self.menuval = {}               #menu values
        self.cachemode = "global"       #cachemode, allowed: "global", "static", "user"
        self.cache = {}                 #cached popup text
        self.cachere = {}               #boolean to show if any changes were made since last cache
        
        self.editlang = "default"
        self.lines["default"] = {}
        self.cache["default"] = "Uncached %s"%self.name
        self.cachere["default"] = False
        
        self.type = "popup"
    def __repr__(self):
        '''
        Representation
        '''
        return 'Popup("%s")'%self.name
    def checklang(self, lang=None):
        '''
        INTERNAL
        Checks if the current editlang exists and if not,
        creates structures for it
        '''
        if not lang:
            editlang = self.editlang
        else:
            editlang = str(lang)
        es.dbgmsg(1, "Popuplib: checklang %s"%editlang)
        if editlang not in self.lines:
            es.dbgmsg(1, "Popuplib:  NOT FOUND!")
            self.lines[editlang] = self.lines["default"].copy()
            self.cache[editlang] = str(self.cache["default"])
            self.cachere[editlang] = bool(self.cachere["default"])
    def information(self, listlevel):
        '''
        Output information about this popup to server console
        '''
        if listlevel >= 1:
            es.dbgmsg(0, " ")
        es.dbgmsg(0, self.name)
        if listlevel >= 1:
            es.dbgmsg(0, "  Type:         "+str(self.type))
            es.dbgmsg(0, "  Lines:        "+str(len(self.lines)))
            es.dbgmsg(0, "  Prepuser:     "+str(self.prepuser))
            es.dbgmsg(0, "  Menuselect:   "+str(self.menuselect))
            es.dbgmsg(0, "  Menuselectfb: "+str(self.menuselectfb))
        if listlevel >= 2:
            es.dbgmsg(0, "  Select:       "+str(len(self.p_select)))
            for item in self.p_select:
                es.dbgmsg(0,"    ["+str(item)+"]:  "+str(self.p_select[item]))
            es.dbgmsg(0, "  Submenu:      "+str(len(self.p_submenu)))
            for item in self.p_submenu:
                es.dbgmsg(0,"    ["+str(item)+"]:  "+str(self.p_submenu[item]))
        if listlevel >= 3:
            es.dbgmsg(0, "  Menuvalue:    "+str(len(self.menuvar)))
            for item in self.menuvar:
                es.dbgmsg(0,"    ["+str(item)+"]:  "+str(self.menuvar[item])+'="'+str(self.menuval[item])+'"')
        if listlevel >= 2:
            es.dbgmsg(0, "  Cachemode:    "+str(self.cachemode))
            es.dbgmsg(0, "  Cachere:      "+str(self.cachere))
            es.dbgmsg(0, "  Displaymode:  "+str(self.displaymode))
        if listlevel >= 3:
            es.dbgmsg(0, "  Current content:")
            for lang in self.lines:
                es.dbgmsg(0, "   Language: %s"%lang)
                for line in self.lines[lang]:
                    es.dbgmsg(0, str(self.lines[lang][line]))
        if listlevel >= 4:
            es.dbgmsg(0, "  Current globally cached content:")
            for lang in self.cache:
                es.dbgmsg(0, "   Language: %s"%lang)
                cc = self.cache[lang].split("\n")
                for line in cc:
                    es.dbgmsg(0, line)
    def isValidLine(self, line, editlang):
        '''
        INTERNAL
        checks if the line in question is valid for editing
        '''
        if (line < 1): return False
        if (line > len(self.lines[editlang])): return False
        return True
    def isValidItem(self, line):
        '''
        INTERNAL
        checks if the item in question is valid menu choice
        '''
        if (line < 1): return False
        if (line > 10): return False
        return True
    def addline(self, text, lang=None):
        '''
        add a line of text to the end of the list
        '''
        if isinstance(text, dict):
            # Assume it is a dict-type object that has languages as keys
            for editlang in text:
                self.checklang(editlang)
                self.lines[editlang][len(self.lines[editlang])+1] = strutfcode(text[editlang])
                self.cachere[editlang]=True
        else:
            if not lang:
                editlang = self.editlang
            else:
                editlang = str(lang)
            self.checklang(editlang)
            self.lines[editlang][len(self.lines[editlang])+1]=strutfcode(text)
            self.cachere[editlang]=True
    def delline(self, line, lang=None):
        '''
        delete a line of text and move subsequent lines
        '''
        if not lang:
            editlang = self.editlang
        else:
            editlang = str(lang)
        self.checklang(editlang)
        if (self.isValidLine(line, editlang)):
            lines = len(self.lines[editlang])
            for thisline in range(line,lines):
                self.lines[editlang][thisline] = self.lines[editlang][thisline+1]
            del self.lines[editlang][lines]
            self.cachere[editlang]=True
        else:
            raise IndexError("Popuplib: Cannot delete line #%d from %s"%(line,self.name))
    def insline(self, line, text, lang=None):
        '''
        insert a line and make room for it
        '''
        if isinstance(text, dict):
            # Assume it is a dict-type object that has languages as keys
            for editlang in text:
                self.checklang(editlang)
                lines = len(self.lines[editlang])
                if (line==lines+1 or self.isValidLine(line,editlang)):
                    for thisline in range(lines+1,line,-1):
                        self.lines[editlang][thisline] = self.lines[editlang][thisline-1]
                    self.lines[editlang][line] = strutfcode(text[editlang])
                    self.cachere[editlang]=True
                else:
                    raise IndexError("Popuplib: Cannot insert line #%d to %s in language %s"%(line,self.name,editlang))
        else:
            if not lang:
                editlang = self.editlang
            else:
                editlang = str(lang)
            self.checklang(editlang)
            lines = len(self.lines[editlang])
            if (line==lines+1 or self.isValidLine(line,editlang)):
                for thisline in range(lines+1,line,-1):
                    self.lines[editlang][thisline] = self.lines[editlang][thisline-1]
                self.lines[editlang][line] = strutfcode(text)
                self.cachere[editlang]=True
            else:
                raise IndexError("Popuplib: Cannot insert line #%d to %s"%(line,self.name))
    def modline(self, line, text, lang=None):
        '''
        modify an existing line
        '''
        if isinstance(text, dict):
            # Assume it is a dict-type object that has languages as keys
            for editlang in text:
                self.checklang(editlang)
                if (self.isValidLine(line,editlang)):
                    self.lines[editlang][line]=strutfcode(text[editlang])
                    self.cachere[editlang]=True
                else:
                    raise IndexError("Popuplib: Cannot modify line #%d in %s in language %s"%(line,self.name,editlang))
        else:
            if not lang:
                editlang = self.editlang
            else:
                editlang = str(lang)
            self.checklang(editlang)
            if (self.isValidLine(line,editlang)):
                self.lines[editlang][line]=strutfcode(text)
                self.cachere[editlang]=True
            else:
                raise IndexError("Popuplib: Cannot modify line #%d in %s"%(line,self.name))
    def addlineAll(self, text):
        for lang in self.lines:
            self.addline(text, lang)
    def dellineAll(self, line):
        for lang in self.lines:
            try:
                self.delline(line, lang)
            except IndexError:
                pass
    def inslineAll(self, line, text):
        for lang in self.lines:
            try:
                self.insline(line, text, lang)
            except IndexError:
                pass
    def modlineAll(self, line, text):
        for lang in self.lines:
            try:
                self.modline(line, text, lang)
            except IndexError:
                pass
    def select(self, item, block):
        '''
        set a select block
        '''
        if (self.isValidItem(item)): self.p_select[item]=block
        else:
            raise IndexError("Popuplib: Invalid menu item %d for select in %s"%(item,self.name))
    def submenu(self, item, menuname):
        '''
        set a submenu
        '''
        if (self.isValidItem(item)):
            if menuname:
                self.p_submenu[item]=menuname
            elif item in self.p_submenu:
                del self.p_submenu[item]
        else:
            raise IndexError("Popuplib: Invalid menu item %d for submenu in %s"%(item,self.name))
    def menuvalue(self, varn, item, varv):
        '''
        set menuvalue
        '''
        if not isinstance(item,int):
            a = str(item)
            item = int(varn)
            varn = a
        if (self.isValidItem(item)):
            self.menuvar[item]=varn
            self.menuval[item]=varv
        else:
            raise IndexError("Popuplib: Invalid menu item %d for menuvalue in %s"%(item,self.name))
    def recache(self, users=[]):
        '''
        recache the popup
        '''
        es.dbgmsg(1,"Popuplib: recache(users="+str(users)+str(type(users))+")")
        try:
            user = int(users)
            userlang = self.i_userlang(user)
            if userlang:
                self.cache[userlang] = self.i_recache(userlang)
                self.cachere[userlang] = False
                gUsers[user].cache[self.name]=self.cache[userlang]
        except TypeError:
            cachedlangs = []
            for user in users:
                userlang = self.i_userlang(int(user))
                if userlang:
                    if not userlang in cachedlangs:
                        self.cache[userlang] = self.i_recache(userlang)
                        cachedlangs.append(userlang)
                    gUsers[int(user)].cache[self.name]=self.cache[userlang]
    def i_recache(self, userlang):
        '''
        INTERNAL
        do the actual construction
        '''
        if self.isRadioMenu():
            # Game supports normal popups, create menu display text
            es.dbgmsg(1,"Popuplib: i_recache menu (%s)"%userlang)
            build = ""
            for line in self.lines[userlang]:
                build += self.lines[userlang][line] + "\n"
            if len(build) > 0:
                build = build[0:-1]         #remove the last \n
            es.dbgmsg(1,'Popuplib: i_recache returns "'+build+'"')
            return build
        else:
            # Game does not support popups, create VGUI dialog instead
            es.dbgmsg(1,"Popuplib: i_recache vgui (%s)"%userlang)
            menuitems = dict()
            build = ""
            for line in self.lines[userlang]:
                text = self.lines[userlang][line]
                try:
                    if text[:2] == '->':
                        choice = int(float(text[2:4]))
                        item = text[3+len(str(choice)):]
                    else:
                        choice = int(float(text[:2]))
                        item = text[1+len(str(choice)):]
                    if choice < 0 or choice > 10:
                        raise ValueError('Only range 0..10 allowed')
                    if choice == 0:
                        choice = 10
                    menuitems[choice] = {
                        'text': item,
                        'command': 'menuselect %d'%choice
                        }
                except ValueError:
                    build += text + "\n"
            if len(build) > 0:
                build = build[0:-1]         #remove the last \n
            if len(menuitems):
                dlg = msglib.VguiDialog(title=self.vguititle,
                                        msg=build,
                                        mode=msglib.VguiMode.MENU)
                for choice in menuitems:
                    dlg.addOption(menuitems[choice]['text'],
                                  menuitems[choice]['command'])
                return dlg
            else:
                dlg = msglib.VguiDialog(title=self.vguititle,
                                        msg=build,
                                        mode=msglib.VguiMode.TEXT)
                return dlg
            
    def checkCache(self, userid):
        '''
        INTERNAL (semi)
        check the cache status and recache as necessary
        '''
        es.dbgmsg(1,"Popuplib: checkCache(userid="+str(userid)+str(type(userid))+")")
        userlang = self.i_userlang(int(userid))
        if not userlang:
            return "Empty popup!"
        es.dbgmsg(1,'Popuplib: userlang="%s"'%userlang)
        es.dbgmsg(1,'Popuplib: cachemode="'+str(self.cachemode)+str(type(self.cachemode))+'"')
        es.dbgmsg(1,'Popuplib: cachere="'+str(self.cachere[userlang])+str(type(self.cachere[userlang]))+'"')

        new_radio_menu = self.isRadioMenu()
        es.dbgmsg(1, 'Popuplib: new_radio_menu = %s'%new_radio_menu)
        es.dbgmsg(1, 'Popuplib: _cached_radio_menu = %s'%self._cached_radio_menu)
        if self._cached_radio_menu != new_radio_menu:
            for l in list(self.cachere.keys()):
                self.cachere[l] = True
            if self.name in gUsers[userid].cache:
                del gUsers[userid].cache[self.name]
            self._cached_radio_menu = new_radio_menu
        
        if self.cachemode == "global" and self.cachere[userlang]:
            es.dbgmsg(1,'Popuplib: Issuing recache on global popup language %s'%userlang)
            self.recache(userid)
        if self.cachemode != "user":
            es.dbgmsg(1,'Popuplib: Not user-specific, returning cache="'+str(self.cache[userlang])+'"'+str(type(self.cache[userlang])))
            return self.cache[userlang]
        else:
            es.dbgmsg(1,'Popuplib: User specific popup')
            if not (self.name in gUsers[userid].cache):
                es.dbgmsg(1,'Popuplib: Popup not in user cache, recaching')
                self.recache(userid)
            return gUsers[userid].cache[self.name]
    
    def handleChoice(self, choice, userid):
        '''
        handle menu choice as a result of client command
        '''
        es.dbgmsg(1, "Popuplib: popup.handleChoice ("+str(choice)+str(type(choice))+", "+str(userid)+str(type(userid))+")")
        user=gUsers[userid]     # retrieve user object
        user.processing = self
        self.processing = True
        es.dbgmsg(1, "Popuplib: displaymode='"+str(self.displaymode)+"'"+str(type(self.displaymode)))
        activeid = user.activeid
        # check displaymode initially
        if self.displaymode == "sticky":
            issticky=True
        else:
            issticky=False
        
        #set server variables for non-python scripts
        es.set('_popup_userid',userid,"User of the popup")
        es.set('_popup_choice',choice,"Menu item chosen")
        es.set('_popup_name',self.name,"Active menu name")

        #check for menuvalue
        if choice in self.menuvar:
            es.set(self.menuvar[choice],self.menuval[choice])

        #check for select block
        pselect = None
        if choice in self.p_select:
            pselect = self.p_select[choice]
            if pselect:
                es.dbgmsg(1, "Popuplib: Select found")
                es.dbgmsg(1, "Popuplib: select block='"+str(pselect)+"'"+str(type(pselect)))
                if isinstance(pselect, collections.Callable):
                    _call_func(pselect, userid, choice, self.name, 'select')
                else:
                    es.doblock(pselect)
                issticky=False

        #check for menuselect block
        if self.menuselect:
            es.dbgmsg(1, "Popuplib: menuselect='"+str(self.menuselect)+"'"+str(type(self.menuselect)))
            if isinstance(self.menuselect, collections.Callable):
                _call_func(self.menuselect, userid, choice, self.name, 'menuselect')
            else:
                es.doblock(self.menuselect)

        #check for menuselectfb block if select block was not used
        if not pselect and self.menuselectfb:
            es.dbgmsg(1, "Popuplib: menuselectfb='"+str(self.menuselectfb)+"'"+str(type(self.menuselectfb)))
            if isinstance(self.menuselectfb, collections.Callable):
                _call_func(self.menuselectfb, userid, choice, self.name, 'menuselectfb')
            else:
                es.doblock(self.menuselectfb)

        #check for submenu
        if choice in self.p_submenu:
            psubmenu = self.p_submenu[choice]
            es.dbgmsg(1, "Popuplib: Submenu found")
            es.dbgmsg(1, "Popuplib: submenu='"+str(psubmenu)+"'"+str(type(psubmenu)))
            if isinstance(psubmenu, Popup_base):
                subp = psubmenu
            else:
                subp = find(psubmenu)
            if subp:
                user.queue[activeid] = subp
            else:
                es.dbgmsg(0, 'Popuplib: Submenu "%s" for popup "%s" not found!'%(
                    str(psubmenu), self.name))
            issticky=False
        
        user.processing = None
        self.processing = False

        #check if the popup was sticky and no custom thing was set to menu item
        if issticky:
            es.dbgmsg(1, "Popuplib: Sending sticky key")
            es.cexec(userid, "slot"+str(choice))
            gamethread.delayed(.2, user.updatePopup, self)
        else:
            #popup finished, fire event and process user queue
            es.event("initialize","popup_select")
            es.event("setint","popup_select","userid",userid)
            es.event("setstring","popup_select","popup_name",self.name)
            es.event("setint","popup_select","popup_choice",choice)
            es.event("fire","popup_select")
            if user.active == self:
                es.dbgmsg(1, "Popuplib: Redoing user queue")
                user.active = None
                user.handleQueue()
            else:
                if activeid in user.queue:
                    del user.queue[activeid]
                if user.active:
                    user.updatePopup(user.active)


class Easymenu_option:
    '''
    A helper class for easymenu options
    '''
    def __init__(self, item, text, state, index):
        self.value = item
        self.text = strutfcode(text)
        self.state = state
        self.index = index

class Popup_easymenu(Popup_base):
    '''
    Popup easymenu allowing easy construction of multi-page menus
    '''
    def __init__(self, pPopupid, pVar, pBlock):
        '''
        Initialize the popup by creating necessary attributes
        with their default values
        '''
        Popup_base.__init__(self, pPopupid)
        self.options = {}
        self.c_savevar = pVar
        self.descriptiond = {}
        self.c_stateformat = {}
        if self.isRadioMenu():
            self.c_stateformat[False] = "%1. %2"
            self.c_stateformat[True] = "->%1. %2"
            self.c_titleformat = _pnformat(pPopupid,30)
            self.c_pageformat = "->%1. %2"
            self.c_exitformat = "0. %2"
        else:
            self.c_stateformat[False] = "(%2)"
            self.c_stateformat[True] = "%2"
            self.c_titleformat = _pnformat(pPopupid,20)
            self.c_pageformat = "%2"
            self.c_exitformat = "%2"
        self.l_titleformat = {}
        self.c_beginsep = "-----------------------------"
        self.c_pagesep = "-----------------------------"
        self.c_endsep = ""
        #self.c_language = gLanguage
        self.p_submenu = None
        self.menuselect = ""
        self.menuselectfb = pBlock
        self.cachemode = "easymenu"
        self.cache = {}
        self.cachere = {}
        self.type = "easymenu"
        self.radio_options_1 = 9
        self.radio_options = 7
        self.vgui_options_1 = 8
        self.vgui_options = 6
        self.default_state = 1
        self.activepage = {}
        self.checklang()
        
    def __repr__(self):
        '''
        Representation
        '''
        return 'Easymenu("%s")'%self.name
    def setdescription(self, desc, lang=None):
        '''
        Set the description for the easymenu
        '''
        if isinstance(desc, dict):
            # Language object
            for editlang in desc:
                self.checklang(editlang)
                self.descriptiond[editlang] = str(desc[editlang])
        else:
            if not lang:
                editlang = self.editlang
            else:
                editlang = str(lang)
            self.checklang(editlang)
            self.descriptiond[editlang] = str(desc)
    def settitle(self, desc, pagenumbers=30, lang=None):
        '''
        Set the title for the easymenu
        '''

        if isinstance(desc, dict):
            # Language object
            for editlang in desc:
                self.l_titleformat[editlang] = _pnformat(str(desc[editlang]), int(pagenumbers))
                self.checklang(editlang)
        else:
            if not lang:
                editlang = self.editlang
            else:
                editlang = str(lang)
            self.l_titleformat[editlang] = _pnformat(str(desc), int(pagenumbers))
            self.checklang(editlang)
    
    def checklang(self, lang=None):
        '''
        INTERNAL
        Checks if the current language exists and create it as necessary
        '''
        if not lang:
            editlang = self.editlang
        else:
            editlang = str(lang)
        es.dbgmsg(1,'Popuplib: easymenu(%s).checklang(%s)'%(self.name,editlang))
        es.dbgmsg(1,'Popuplib: c_titleformat="%s"'%str(self.c_titleformat))
        if editlang not in self.options:
            es.dbgmsg(1,'Popuplib: language not used yet, creating...')
            if editlang == "default":
                self.options[editlang] = {}
                self.cache[editlang] = {}
                self.cachere[editlang] = {1:True}
                self.descriptiond[editlang] = ""
            else:
                self.options[editlang] = self.options["default"].copy()
                self.cache[editlang] = {}
                self.cachere[editlang] = {}
                for pagenum in range(self.getPageCount(editlang)):
                    self.cachere[editlang][pagenum+1] = True
                self.descriptiond[editlang] = str(self.descriptiond["default"])
                if not editlang in self.l_titleformat and "default" in self.l_titleformat:
                    self.l_titleformat[editlang] = str(self.l_titleformat["default"])
    
    def information(self, listlevel):
        '''
        Print out some information to server console
        '''
        es.dbgmsg(0, self.name)
        if listlevel >= 1:
            es.dbgmsg(0, "  Type:         "+str(self.type))
            es.dbgmsg(0, "  Variable:     "+str(self.c_savevar))
            es.dbgmsg(0, "  Options:      "+str(len(self.options[gLanguage])))
            es.dbgmsg(0, "  Menuselect:   "+str(self.menuselect))
            es.dbgmsg(0, "  Menuselectfb: "+str(self.menuselectfb))
    
    def addoption(self, item, text, state=None, lang=None):
        '''
        Add a new option to the menu
        '''
        if not isinstance(text, dict):
            es.dbgmsg(1, "Popuplib.py: addoption detected text object")
            if not lang:
                editlang = self.editlang
            else:
                editlang = str(lang)
            text = {editlang: text}
        else:
            # Assume as dict-type object with language names as keys
            es.dbgmsg(1, "Popuplib.py: addoption detected language object")
        for editlang in text:
            self.checklang(editlang)
            index = len(self.options[editlang])+1
            if state == None:
                state = self.default_state
            self.options[editlang][index]=Easymenu_option(item, text[editlang], state, index)
            self.cachere[editlang][self.getPageNumber(len(self.options[editlang]), editlang)]=True
            if index == self.radio_options_1+1:
                self.cachere[editlang][1] = True
                # first page needs caching also when moving to page 2
                
    
    def findOption(self, item, lang=None):
        '''
        INTERNAL
        Find option by its value
        '''
        if not lang:
            editlang = self.editlang
        else:
            editlang = str(lang)
        self.checklang(editlang)
        for i in self.options[editlang]:
            opt = self.options[editlang][i]
            if opt.value == item: return opt
        return None
    
    def setoption(self, item, text=None, state=None, lang=None):
        '''
        Edit an existing option
        '''
        if not lang:
            editlang = self.editlang
        else:
            editlang = str(lang)
        if editlang == "default":
            langs = list(self.options.keys())
            ignore_error = len(langs)-1
        else:
            langs = [editlang]
            ignore_error = 0
        for editlang in langs:
            self.checklang(editlang)
            opt = self.findOption(item, editlang)
            if opt:
                self.cachere[editlang][self.getPageNumber(opt.index, editlang)]=True
                if text:
                    opt.text = strutfcode(text)
                if state:
                    opt.state = state
            else:
                if not ignore_error:
                    raise IndexError("Popuplib: Option %s does not exist in easymenu %s"%(item,self.name))
                else:
                    ignore_error -= 1
    
    def getPageNumber(self, option, language):
        '''
        INTERNAL
        Returns the page number on which the option is present in
        '''
        opts = len(self.options[language])
        if self.isRadioMenu():
            if opts <= self.radio_options_1: return 1
            return int(math.ceil(float(option)/self.radio_options))
        else:
            if opts <= self.vgui_options_1: return 1
            return int(math.ceil(float(option)/self.vgui_options))
    
    def submenu(self, item, menuname=None):
        '''
        set a submenu for menuselect 10
        '''
        if not menuname:
            menuname = item
        self.p_submenu = menuname
    
    def recache(self, users=[], pages=None):
        '''
        recache the popup
        '''
        es.dbgmsg(1,"Popuplib: recache(users="+str(users)+str(type(users))+")")
        try:
            user = int(users)
            userlang = self.i_userlang(user)
            es.dbgmsg(1,"Popuplib: compatible user language: %s"%str(userlang))
            if userlang:
                if not pages:
                    pages = list(range(1,self.getPageNumber(len(self.options[userlang]), userlang)+1))
                self.i_recache(pages, userlang)
                gUsers[user].cache[self.name]=self.cache[userlang]
        except TypeError:
            cachedlangs = []
            for user in users:
                userlang = self.i_userlang(int(user))
                es.dbgmsg(1,"Popuplib: compatible user %d language: %s"%(int(user),str(userlang)))
                if userlang:
                    if not userlang in cachedlangs:
                        if not pages:
                            pages = list(range(1,self.getPageNumber(len(self.options[userlang]), userlang)+1))
                        self.cache[userlang] = self.i_recache(pages, userlang)
                        cachedlangs.append(userlang)
                    gUsers[int(user)].cache[self.name]=self.cache[userlang]
    def i_recache(self, pages, userlang):
        '''
        INTERNAL
        do the actual construction
        '''
        if userlang not in self.l_titleformat:
            self.l_titleformat[userlang] = str(self.c_titleformat)
        es.dbgmsg(1,"Popuplib: %s easymenu i_recache(%s)"%(self.name,userlang))
        maxindex = len(self.options[userlang])
        totalpages = self.getPageNumber(maxindex, userlang)
        if self.isRadioMenu():
            self.i_recacheRadio(pages, userlang, maxindex, totalpages)
        else:
            self.i_recacheVGUI(pages, userlang, maxindex, totalpages)

    def i_recacheVGUI(self, pages, userlang, maxindex, totalpages):
        '''
        INTERNAL
        recache VGUI easymenu
        '''
        if totalpages == 1:
            maxline=self.vgui_options_1
        else:
            maxline=self.vgui_options
        
        for page in pages:
            title = str(self.l_titleformat[userlang]).replace("%p", str(page))
            title = title.replace("%t", str(totalpages))
            if self.descriptiond[userlang]:
                description = str(self.descriptiond[userlang])
            else:
                description = title
            dlg = msglib.VguiDialog(title=title,
                                    msg = description,
                                    mode = msglib.VguiMode.MENU)
            for line in range(1,maxline+1):
                index = (page-1)*self.vgui_options+line
                if index <= maxindex:
                    opt = self.options[userlang][index]
                    thisformat = str(self.c_stateformat[bool(opt.state)])
                    thisformat = thisformat.replace("%1", str(line)).replace("%2", str(opt.text))
                    dlg.addOption(thisformat, "menuselect %d"%line)
                else:
                    dlg.addOption("", "menuselect %d"%line)
            if page > 1:
                dlg.addOption(
                    str(self.c_pageformat).replace("%1", "7").replace("%2", langdata[userlang]['prev']),
                    "menuselect 8")
            elif totalpages > 1:
                dlg.addOption("", "menuselect 8")
            if page < totalpages:
                dlg.addOption(
                    str(self.c_pageformat).replace("%1", "8").replace("%2", langdata[userlang]['next']),
                    "menuselect 9")
            elif totalpages > 1:
                dlg.addOption("", "menuselect 9")
            self.cache[userlang][page] = dlg
            self.cachere[userlang][page] = False

    def i_recacheRadio(self, pages, userlang, maxindex, totalpages):
        '''
        INTERNAL
        Recache RADIO style easymenu
        '''
        if totalpages == 1:
            maxline=self.radio_options_1
        else:
            maxline=self.radio_options
        for page in pages:
            build = self.pageformatstart(page,totalpages,userlang)
            for line in range(1,maxline+1):
                index = (page-1)*self.radio_options+line
                if index <= maxindex:
                    opt = self.options[userlang][index]
                    thisformat = str(self.c_stateformat[bool(opt.state)])
                    thisformat = thisformat.replace("%1", str(line)).replace("%2", str(opt.text))
                    build += thisformat + "\n"
                else:
                    build += " \n"
            build += self.pageformatend(page,totalpages,self.i_endlangg(userlang))
            self.cache[userlang][page] = build
            self.cachere[userlang][page] = False
                
    def pageformatstart(self, page, total, language):
        '''
        INTERNAL
        Formats the start of a page
        '''
        es.dbgmsg(1,"Popuplib: pageformatstart for page %d/%d in lang %s"%(page,total,language))
        build = str(self.l_titleformat[language]).replace("%p", str(page))
        build = build.replace("%t", str(total)) + "\n"
        if self.descriptiond[language]:
            build += str(self.descriptiond[language]) + "\n"
        if self.c_beginsep:
            build += str(self.c_beginsep) + "\n"
        return build
    def pageformatend(self, page, total, language):
        '''
        INTERNAL
        Formats the end of a page
        '''
        if total > 1:
            tight = False
        else:
            tight = True
        build = ""
        if self.c_pagesep:
            build += str(self.c_pagesep) + "\n"
        if page > 1: build += str(self.c_pageformat).replace("%1", "8").replace("%2", langdata[language]['prev'])+"\n"
        elif not tight: build += " \n"
        if page < total: build += str(self.c_pageformat).replace("%1", "9").replace("%2", langdata[language]['next'])+"\n"
        elif not tight: build += " \n"
        if self.c_endsep:
            build += str(self.c_endsep) + "\n"
        build += str(self.c_exitformat).replace("%1", "10").replace("%2", langdata[language]['quit'])
        return build
    def sendPage(self, users, pagenumber):
        '''
        Sets active page and sends the menu to users
        '''
        if pagenumber:
            try:
                userid = int(users)
                userlist = [userid]
            except TypeError:
                userlist = list(users)
            for userid in userlist:
                self.activepage[int(userid)]=pagenumber
        self.send(users)
    def getPage(self, userid):
        '''
        Returns the page number the user has active
        '''
        return self.activepage[int(userid)]
    def unsendPage(self, users, pagenumber):
        '''
        Unsends the easymenu from users that have the specified page active
        '''
        try:
            userid = int(users)
            userlist = [userid]
        except TypeError:
            userlist = list(users)
        for userid in userlist:
            if self.activepage[int(userid)]==pagenumber:
                self.unsend(userid)
    def getPageCount(self, userlang=None):
        '''
        Returns the number of pages
        '''
        if not userlang: userlang = self.editlang
        if userlang == "default": userlang = gLanguage
        return self.getPageNumber(len(self.options[userlang]), userlang)
        
    def checkCache(self, userid):
        '''
        INTERNAL (semi)
        check the cache status and recache as necessary
        '''
        if not gUsers[int(userid)]:
            return None
        if int(userid) in self.activepage:
            page = self.activepage[int(userid)]
        else:
            page = 1
            self.activepage[int(userid)] = 1
        es.dbgmsg(1,"Popuplib: checkCache(userid="+str(userid)+str(type(userid))+")")
        es.dbgmsg(1,"Popuplib: checkCache(page="+str(page)+str(type(page))+")")
        es.dbgmsg(1,'Popuplib: cachemode="'+str(self.cachemode)+str(type(self.cachemode))+'"')
        userlang = self.i_userlang(int(userid))
        es.dbgmsg(1,'Popuplib: effective language=%s'%userlang)
        
        new_radio_menu = self.isRadioMenu()
        if self._cached_radio_menu != new_radio_menu:
            for l in self.cachere:
                for pagenum in self.cachere[l]:
                    self.cachere[l][pagenum] = True
            if self.name in gUsers[userid].cache:
                del gUsers[userid].cache[self.name]
            self._cached_radio_menu = new_radio_menu
        
        if self.cachemode == "easymenu" and self.cachere[userlang][page]:
            es.dbgmsg(1,"Popuplib: recache")
            self.recache(userid,[page])
        elif self.cachemode == "construct":
            es.dbgmsg(1,"Popuplib: recache CONSTRUCT!")
            if self.construct(self):
                self.recache(userid)
        pages = self.getPageNumber(len(self.options[userlang]), userlang)
        if page < 1:
            page = 1
        elif page > pages:
            page = pages
        self.activepage[int(userid)] = page
        if self.cachemode != "user":
            es.dbgmsg(1,'Popuplib: Not user-specific, returning cache="'+str(self.cache[userlang][int(page)])+str(type(self.cache[userlang][int(page)]))+'"')
            return self.cache[userlang][int(page)]
        else:
            es.dbgmsg(1,'Popuplib: User specific popup')
            if not (self.name in gUsers[userid].cache):
                es.dbgmsg(1,'Popuplib: Popup not in user cache, recaching')
                self.recache(userid,[page])
            return gUsers[userid].cache[self.name][int(page)]
    
    def handleChoice(self, choice, userid):
        '''
        handle menu choice as a result of client command
        '''
        es.dbgmsg(1, "Popuplib: easymenu.handleChoice ("+str(choice)+str(type(choice))+", "+str(userid)+str(type(userid))+")")
        userlang = self.i_userlang(int(userid))
        user=gUsers[userid]     # retrieve user object
        user.processing = self
        self.processing = True
        activeid = user.activeid
        page = self.activepage[int(userid)]
        pages = self.getPageNumber(len(self.options[userlang]), userlang)
        es.dbgmsg(1, "Popuplib: page "+str(page)+"/"+str(pages))
        choices = len(self.options[userlang])
        es.dbgmsg(1, "Popuplib: choice "+str(choice)+"/"+str(choices))
        varvalindex = self.radio_options*(page-1)+choice
        es.dbgmsg(1, "Popuplib: index="+str(varvalindex))
        validchoice = False
        
        #set server variables for non-python scripts
        es.set('_popup_userid',userid,"User of the popup")
        es.set('_popup_choice',choice,"Menu item chosen")
        es.set('_popup_name',self.name,"Active menu name")
        if varvalindex <= choices:
            opt = self.options[userlang][varvalindex]
            if opt.state:
                choiceval = opt.value
                if pages > 1 and choice < 8:
                    validchoice = True
                elif pages == 1 and choice < 10:
                    validchoice = True
        if not validchoice:
            choiceval = choice
        else:
            if self.c_savevar:
                es.set(self.c_savevar,str(choiceval),"Chosen object")
            del self.activepage[int(userid)]

        #check for menuselect block
        if self.menuselect:
            es.dbgmsg(1, "Popuplib: menuselect='"+str(self.menuselect)+"'"+str(type(self.menuselect)))
            if isinstance(self.menuselect, collections.Callable):
                _call_func(self.menuselect, userid, choiceval, self.name, 'menuselect')
            else:
                es.doblock(self.menuselect)

        #check for menuselectfb block if valid user
        if validchoice and self.menuselectfb:
            es.dbgmsg(1, "Popuplib: menuselectfb='"+str(self.menuselectfb)+"'"+str(type(self.menuselectfb)))
            if isinstance(self.menuselectfb, collections.Callable):
                _call_func(self.menuselectfb, userid, choiceval, self.name, 'menuselectfb')
            else:
                es.doblock(self.menuselectfb)

        #check for submenu (=send popup again and change page if applicable)
        if not validchoice and choice < 10:
            if pages > 1:
                if choice > 7:
                    if choice == 8:
                        page -= 1
                        if page == 0:
                            page = 1
                    else:
                        page += 1
                        if page > pages:
                            page = pages
                    self.activepage[int(userid)] = page
            user.queue[activeid] = self
        elif choice == 10:
            del self.activepage[int(userid)]
            if self.p_submenu:
                if isinstance(self.p_submenu, Popup_base):
                    user.queue[activeid] = self.p_submenu
                else:
                    user.queue[activeid] = find(self.p_submenu)

        #popup finished, fire event and process user queue
        es.event("initialize","popup_select")
        es.event("setint","popup_select","userid",userid)
        es.event("setstring","popup_select","popup_name",self.name)
        es.event("setint","popup_select","popup_choice",choice)
        es.event("fire","popup_select")
        user.processing = None
        self.processing = False
        if user.active == self:
            es.dbgmsg(1, "Popuplib: Redoing user queue")
            user.active = None
            user.handleQueue()
        else:
            if activeid in user.queue:
                del user.queue[activeid]
            if user.active:
                user.updatePopup(user.active)

class Popup_list(Popup_easymenu):
    '''
    Easymenu like structure that shows 10 non-selectable numbered items per page
    '''
    def __init__(self, pPopupid, options=10):
        '''
        Initialize easylist
        '''
        super(Popup_list, self).__init__(pPopupid, None, None)
        self.radio_options_1 = options
        self.radio_options = options
        self.vgui_options_1 = options
        self.vgui_options = options
        self.type = "easylist"
        self.default_state = 0

    def additem(self, text, value=None, state=None, lang=None):
        '''
        Add an item to the easylist
        '''
        self.addoption(value, text, state, lang)
    
    def i_recacheVGUI(self, pages, userlang, maxindex, totalpages):
        '''
        INTERNAL
        recache VGUI easylist (overrides easymenu method)
        '''
        if totalpages == 1:
            maxline=self.vgui_options_1
        else:
            maxline=self.vgui_options
        
        for page in pages:
            title = str(self.l_titleformat[userlang]).replace("%p", str(page))
            title = title.replace("%t", str(totalpages))
            if self.descriptiond[userlang]:
                description = str(self.descriptiond[userlang])
            else:
                description = title
            for line in range(1,maxline+1):
                index = (page-1)*self.vgui_options+line
                if index <= maxindex:
                    opt = self.options[userlang][index]
                    thisformat = str(self.c_stateformat[bool(opt.state)])
                    thisformat = thisformat.replace("%1", str(line)).replace("%2", str(opt.text))
                    description += "\n" + thisformat
            
            dlg = msglib.VguiDialog(title=title,
                                    msg = description,
                                    mode = msglib.VguiMode.MENU)
            if page > 1:
                dlg.addOption(
                    str(self.c_pageformat).replace("%1", "7").replace("%2", langdata[userlang]['prev']),
                    "menuselect 8")
            elif totalpages > 1:
                dlg.addOption("", "menuselect 8")
            if page < totalpages:
                dlg.addOption(
                    str(self.c_pageformat).replace("%1", "8").replace("%2", langdata[userlang]['next']),
                    "menuselect 9")
            elif totalpages > 1:
                dlg.addOption("", "menuselect 9")
            self.cache[userlang][page] = dlg
            self.cachere[userlang][page] = False
                 

class Popup_user(object):
    '''
    INTERNAL class
    that stores information about a player, mainly their popup queue
    '''
    def __init__(self, userid):
        '''
        Initialize the player info
        '''
        self.userid = userid        #save the userid
        self.queue = {}             #empty popup queue
        self.active = None          #no active popup currently
        self.activeid = 0           #active queue id
        self.nextindex = 1          #next queue index
        self.cache = {}             #popup cache
        self.prioritized = False    #used for queue priorization
        self.language = gLanguage   #user language
        self.updateLanguage()
        self.closemode = False      #close mode
        self.processing = None      #popup in processing
    
    def updateLanguage(self):
        '''
        Update the language info
        '''
        userobject = playerlib.getPlayer(self.userid)
        language = userobject.get('lang')
        es.dbgmsg(1,'Popuplib: User %d language="%s"'%(self.userid, language))
        if language: self.language=language
        
    def handleQueue(self):
        '''
        Display the next popup in player's queue!!!11!!1
        '''
        es.dbgmsg(1, "Popuplib: User.handleQueue(userid:"+str(self.userid)+")")
        es.dbgmsg(1, "Popuplib: activeid="+str(self.activeid)+str(type(self.activeid)))
        es.dbgmsg(1, "Popuplib: queue="+str(self.queue)+"("+str(len(self.queue))+" items)")
        if self.active == None and len(self.queue) > 0:
            #player doesn't have active popup but has some in queue = display next
            gUsers.haspopup(self)
            qindex = min(self.queue)
            qpopup = self.queue[qindex]
            es.dbgmsg(1, "Popuplib: qindex='"+str(qindex)+"'"+str(type(qindex)))
            es.dbgmsg(1, "Popuplib: qpopup='"+str(qpopup)+"'"+str(type(qpopup)))
            del self.queue[qindex]      #delete popup from queue
            es.dbgmsg(1, "Popuplib: queue after="+str(self.queue)+"("+str(len(self.queue))+" items)")
            prepuser = qpopup.prepuser
            es.dbgmsg(1, "Popuplib: prepuser='"+str(prepuser)+"'"+str(type(prepuser)))
            if isinstance(prepuser, collections.Callable):
                #python function for prepuser :D
                prepuser(self.userid, qpopup.name)
            elif prepuser != "":
                #regular es block for prepuser
                es.set('_popup_userid',self.userid)
                es.set('_popup_name',qpopup.name)
                #es.doblock(prepuser) <- does not work :(
                es.server.cmd("es_xdoblock "+str(prepuser))
                #the popup might be recreated in the prepuser block, reload it:
                qpopup = gPopups[qpopup.name]

            #get the popup properties and display it to user
            menudisplay = qpopup.checkCache(self.userid)
            timeout = qpopup.timeoutview
            if qpopup.isRadioMenu():
                # in game that supports popups
                pendingcount = len(self.queue)
                if pendingcount > 0:
                    pendingtext = "\n" + ("-"*29)+"\n ("+langdata[gLanguage]['pending'] + ": "+str(pendingcount)+") "
                else:
                    pendingtext = ""
                menudisplay += pendingtext
                es.dbgmsg(1, "Popuplib: menudisplay='"+str(menudisplay)+"'"+str(type(menudisplay)))
                if qpopup.enablekeys:
                    es.menu(timeout, self.userid, menudisplay, qpopup.enablekeys)
                else:
                    es.menu(timeout, self.userid, menudisplay)
                es.dbgmsg(1, 'es.menu(%f, %d, "%s", %s)'%(timeout, self.userid, menudisplay, qpopup.enablekeys))

                #perform timeout check
                if timeout > 0:
                    gamethread.delayedname(timeout, "_popup_"+qpopup.name, unsendid, (qindex, qpopup, self.userid))
                refreshtime = gameSupport[gGamename][1]
                if refreshtime:
                    gamethread.delayed(refreshtime, self.refreshPopup, qpopup)
            else:
                # game that does not support popups, use Vgui instead
                menudisplay.send(self.userid)

            #set active popup info
            self.active = qpopup
            self.activeid = qindex
                
            #fire event popup_display
            es.event("initialize","popup_display")
            es.event("setint","popup_display","userid",self.userid)
            es.event("setstring","popup_display","popup_name",qpopup.name)
            es.event("setfloat","popup_display","popup_timeout",timeout)
            es.event("fire","popup_display")
        elif self.active:
            gUsers.haspopup(self)
            self.updatePopup(self.active)
        else:
            gUsers.hasnopopup(self)
    
    def unsendView(self, index, pobject):
        '''
        remove popup from display if the queue index matches
        '''
        if index == self.activeid and pobject is self.active:
            if self.active.oldskooltov:
                #some older scripts want to receive menuselect 10
                self.active.handleChoice(10, self.userid)
            else:
                #get next popup from queue, if there is one
                self.active = None
                self.handleQueue()
    def unsendSend(self, index):
        '''
        remove popup from queue by queue index
        '''
        if index in self.queue:
            del self.queue[index]
            #update pending counter:
            if self.active:
                self.queue[self.activeid] = self.active
                self.handleQueue()
    
    def unsendName(self, popupid, close=False):
        '''
        remove popups from queue by the name
        '''
        compopup = gPopups[popupid]
        self.unsend(compopup, close)
        
    def unsend(self, compopup, close):
        '''
        remove popups from queue by the class handler
        '''

        # since you cannot delete or add items from dictionary in a loop,
        # create temporary list of the queue indexes for the loop:
        tempqueue = list(self.queue)
        for index in tempqueue:
            if compopup == self.queue[index]:
                del self.queue[index]
        if self.active == compopup and self.active != self.processing:
            #the active one mathced also!
            if close:
                #close mode used, don't process current popup
                self.active = None
                if len(self.queue) > 0:
                    self.handleQueue()
                elif compopup.isRadioMenu():
                    es.dbgmsg(1,"Popuplib: setting closemode to True")
                    self.closemode = True
                    es.cexec(self.userid,"slot10")
            else:
                #close the popup
                es.cexec(self.userid,"slot10")
    
    def isqueued(self, p):
        '''
        return first queue position of the popup
        '''
        if self.active == p: return 1
        go = 1
        if self.queue:
            for index in range(min(self.queue),max(self.queue)+1):
                if index in self.queue:
                    go += 1
                    if self.queue[index] == p:
                        return go
        return 0
    
    def updatePopup(self, p):
        '''
        redisplay the popup if its active
        '''
        es.dbgmsg(1,"Popuplib: Userid"+str(self.userid)+".updatePopup("+str(p)+str(type(p))+")")
        es.dbgmsg(1,"Popuplib: active = "+str(self.active)+str(type(self.active)))
        if self.active and self.active is p:
            es.dbgmsg(1,"Popuplib: match!")
            self.queue[self.activeid] = p
            self.active = None
            self.handleQueue()
            return True
        return False

    def refreshPopup(self, p):
        '''
        Orange Box popup refreshment
        '''
        return self.updatePopup(p)

class UserHolderClass(object):
    '''
    This is an internal class for handling user objects
    '''
    def __init__(self):
        '''
        Create attributes and steal players from server
        '''
        self.userdict = {}
        self.activepopups = set()
        userlist = playerlib.getUseridList("#human")
        for userid in userlist:
            self[int(userid)] = Popup_user(int(userid))
        es.addons.unregisterForEvent(selfmodule, 'es_client_command')
    def __contains__(self, userid):
        '''
        x.__contains__(userid) <-> userid in x
        '''
        try:
            playerlib.getPlayer(userid)
            return True
        except playerlib.UseridError:
            return False
    def __setitem__(self, userid, value):
        '''
        x.__setitem__(userid, value) <-> x[userid] = value
        '''
        self.userdict[int(userid)] = value
    def __getitem__(self, userid):
        '''
        a = x.__getitem__(userid) <-> a = x[userid]
        '''
        if int(userid) not in self.userdict:
            nuser = playerlib.getPlayer(userid)
            if int(nuser.attributes['isbot']) == 0:
                self[int(userid)] = Popup_user(int(userid))
            else:
                return None
        return self.userdict[int(userid)]
    def __delitem__(self, userid):
        '''
        x.__delitem__(userid) <-> del x[userid]
        '''
        if int(userid) in self.userdict:
            del self.userdict[int(userid)]
    def haspopup(self, user):
        '''
        Some player instructs that he has popups in queue or active.
        If this is the first report, register es_client_command event handler
        '''
        es.dbgmsg(1,"Popuplib: haspopup!")
        if len(self.activepopups) == 0:
            es.dbgmsg(1,"Popuplib: register es_client_command")
            es.addons.registerForEvent(selfmodule, 'es_client_command', es_client_command)
        self.activepopups.add(user)
    def hasnopopup(self, user):
        '''
        Some player instructs that he no longer has any popups in queue or active.
        If this is the last report, unregister es_client_command event handler
        '''
        es.dbgmsg(1,"Popuplib: hasnopopup!")
        if user in self.activepopups:
            self.activepopups.remove(user)
            if len(self.activepopups) == 0:
                gamethread.delayed(1, self.checkeventneed)
    def checkeventneed(self):
        '''
        Checks if the es_client_command is still needed
        '''
        if len(self.activepopups) == 0:
            es.dbgmsg(1,"Popuplib: unregister es_client_command")
            es.addons.unregisterForEvent(selfmodule, 'es_client_command')



gUsers = UserHolderClass()

#popup commands begin here
#usage from other Python scripts for example:
#  import es
#  import popuplib
#  a = popuplib.create("insertnamehere")
#  a.addline("Line 1")
#  a.send(es.getuserid("Jonez"))
#  a.delete
def active(userid):
    '''
    check which popup is active and how many are in queue
    '''
    pl = {'name': '0', 'count': 0, 'object': None}
    user = gUsers[int(userid)]
    if not user:
        return None
    if user.active:
        pl['name']=user.active.name
        pl['count']=len(user.queue)+1
        pl['object']=user.active
    return pl
    
def close(pPopupid, pUsers):
    '''
    remove queued popups by the popup name but do not trigger menuselect 10
    '''
    if not isinstance(pPopupid, str):
        for p in pPopupid:
            close(p, pUsers)
    else:
        try:
            userid = int(pUsers)
            user = gUsers[userid]
            if user: user.unsendName(pPopupid, True)
        except TypeError:
            for userid in pUsers:
                user = gUsers[int(userid)]
                if user: user.unsendName(pPopupid, True)

def construct(pPopupid, pList, pFlags, pBlock = None):
    '''
    create a new construct popup
    '''
    if not isinstance(pPopupid, str):
        rv = []
        for p in pPopupid:
            rv.append(construct(p, pList, pFlags, pBlock))
        return rv
    else:
        if pList in gConstructs:
            gPopups[pPopupid] = gConstructs[pList](pPopupid, pFlags, pBlock)
            return gPopups[pPopupid]
        else:
            raise NameError('Construct "%s" not available'%pList)

def create(pPopupid):
    '''
    create a new normal popup
    '''
    if not isinstance(pPopupid, str):
        rv = []
        for p in pPopupid:
            rv.append(create(p))
        return rv
    else:
        if pPopupid in gPopups:
            if gPopups[pPopupid].type == "popup":
                gPopups[pPopupid].__init__(pPopupid)
            else:
                gPopups[pPopupid] = Popup_popup(pPopupid)
        else:
            gPopups[pPopupid] = Popup_popup(pPopupid)
        return gPopups[pPopupid]

def delete(pPopupid):
    '''
    delete a popup
    '''
    if not isinstance(pPopupid, str):
        for p in pPopupid:
            delete(p)
    else:
        if pPopupid in gPopups:
            gamethread.cancelDelayed('_popup_'+pPopupid)
            if gPopups[pPopupid].processing:
                gamethread.queue(_delete, pPopupid)
            else:
                _delete(pPopupid)
        else:
            raise ValueError("Popuplib: Cannot delete popup %s, it does not exist"%pPopupid)

def _delete(pPopupid):
    '''
    internal delete a popup method
    '''
    if pPopupid in gPopups:
        del gPopups[pPopupid]

def easylist(pPopupid, data=None, options=10):
    '''
    create a new easylist popup
    '''
    if not isinstance(pPopupid, str):
        rv = []
        for p in pPopupid:
            rv.append(easylist(p, options))
        return rv
    else:
        if pPopupid in gPopups:
            if gPopups[pPopupid].type == "easylist":
                p = gPopups[pPopupid].__init__(pPopupid, options)
            else:
                p = gPopups[pPopupid] = Popup_list(pPopupid, options)
        else:
            p = gPopups[pPopupid] = Popup_list(pPopupid, options)
        if data:
            for item in data:
                p.additem(item)
        return p

def easymenu(pPopupid, pVarn, pBlock):
    '''
    create a new easymenu popup
    '''
    if not isinstance(pPopupid, str):
        rv = []
        for p in pPopupid:
            rv.append(easymenu(p, pVarn, pBlock))
        return rv
    else:
        if pPopupid in gPopups:
            if gPopups[pPopupid].type == "easymenu":
                gPopups[pPopupid].__init__(pPopupid, pVarn, pBlock)
            else:
                gPopups[pPopupid] = Popup_easymenu(pPopupid, pVarn, pBlock)
        else:
            gPopups[pPopupid] = Popup_easymenu(pPopupid, pVarn, pBlock)
        return gPopups[pPopupid]

def emulate(pPopupid, pItem, pUsers):
    '''
    emulate user doing a menu choice from any existing popup.
    use with caution...
    '''
    try:
        userid = int(pUsers)
        gPopups[pPopupid].handleChoice(int(pItem), userid)
    except TypeError:
        for userid in pUsers:
            gPopups[pPopupid].handleChoice(int(pItem), userid)

def exists(pPopupid):
    '''
    does named popup exist
    '''
    return bool(pPopupid in gPopups)

def find(pPopupid):
    '''
    return class instance of named popup
    '''
    if pPopupid in gPopups:
        return gPopups[pPopupid]
    return None

def isqueued(pPopupid, pUserid):
    '''
    returns the queue position of the named popup
    '''
    if not isinstance(pPopupid, str):
        rv = []
        for p in pPopupid:
            rv.append(isqueued(p, pUserid))
        return rv
    else:
        user = gUsers[pUserid]
        if user and pPopupid in gPopups:
            return user.isqueued(gPopups[pPopupid])

def langstring(prefix, langobject, suffix=''):
    '''
    constructs a language dict by adding prefix and suffix for each element
    '''
    newc = dict()
    for l in langobject:
        newc[l] = "%s%s%s"%(prefix,langobject[l],suffix)
    return newc

def quicksend(pViewtime, pUserid, pText, pBlock="", pKeys=""):
    '''
    like es.menu, but uses popup queue
    '''
    qs = Popup_popup("quicksend")
    qs.timeoutview = pViewtime
    qs.cache['default'] = pText
    qs.menuselect = pBlock
    qs.enablekeys = pKeys
    qs.send(pUserid)

def send(pPopupid, pUserid, prio=False):
    '''
    send a named popup to user/users
    '''
    if not isinstance(pPopupid, str):
        rv = []
        for p in pPopupid:
            rv.append(send(p, pUserid, prio))
        return rv
    else:
        if pPopupid in gPopups:
            gPopups[pPopupid].send(pUserid,prio)
        else:
            raise ValueError("Popuplib: Cannot send popup %s, it does not exist"%pPopupid)

def unsend(pIndex, pUserid):
    '''
    INTERNAL (mostly)
    remove a queued popup by its queue index
    '''
    if pUserid in gUsers:
        gUsers[pUserid].unsendSend(pIndex)
    
def unsendid(pIndex, pObject, pUserid):
    '''
    INTERNAL (mostly)
    remove a visible popup by its queue index
    '''
    if pUserid in gUsers:
        gUsers[pUserid].unsendView(pIndex, pObject)
    
def unsendname(pPopupid, pUsers):
    '''
    remove queued popups by the popup name
    '''
    if not isinstance(pPopupid, str):
        for p in pPopupid:
            rv.append(unsendmane(p, pUsers))
    else:
        try:
            userid = int(pUsers)
            gUsers[userid].unsendName(pPopupid)
        except TypeError:
            for userid in pUsers:
                user = gUsers[int(userid)]
                if user: user.unsendName(pPopupid)
    
def _pnformat(s, n):
    '''
    INTERNAL function for formatting title using page numbering
    '''
    if n>0:
        l = len(s)
        a = max((1,n-l))
        x = "%s%s(%s)"%(s," "*a,"%p/%t")
        return x
    return s

def _call_func(f, u, c, p, t):
    '''
    INTERNAL function for calling external function
    '''
    try:
        f(u,c,p)
    except TypeError as e:
        infuncname = str(e)[:str(e).find('(')]
        if infuncname == f.__name__:
            es.dbgmsg(0,'Invalid %s function "%s" for popup "%s"'%(t, infuncname, p))
            es.dbgmsg(0,'Callback function must accept three parameters')
            es.dbgmsg(1,'Details:')
            es.dbgmsg(1,' Function name: '+f.__name__)
            es.dbgmsg(1,' Function info: '+str(f))
            es.dbgmsg(2,' Full error: '+str(e))
        else:
            es.dbgmsg(0,'Popuplib: Exception when calling function "%s" for popup "%s":'%(f.__name__, p))
            es.excepter(*sys.exc_info())
    except BaseException as e:
        es.dbgmsg(0,'Popuplib: Exception when calling function "%s" for popup "%s":'%(f.__name__, p))
        es.excepter(*sys.exc_info())

def strutfcode(value): 
    """ converts value into utf-8 coded string if it is unicode,
    otherwise forces __str__ """ 
    if type(value).__name__ == 'unicode': 
        return value.encode('utf-8') 
    return str(value)

def updateGameName():
    '''
    checks which Source game server this is and adjusts menu behavior
    based on the game engine
    '''
    global gGamename
    gamename = str(es.ServerVar('eventscripts_gamedir')).replace('\\', '/').rpartition('/')[2].lower()
    if gamename in gameSupport:
        gGamename = gamename
    else:
        gGamename = 'unknown'
    es.dbgmsg(1, 'Popuplib: Detected game folder: "%s"'%gamename)
    es.dbgmsg(1, 'Popuplib: Selected game folder: "%s"'%gGamename)
    es.dbgmsg(1, 'Popuplib: Game support status : %s'%str(gameSupport[gGamename]))

def registerConstruct(name, function):
    '''
    Registers a new construct function to be used with construct()
    '''
    gConstructs[name] = function

def unregisterConstruct(name):
    '''
    Removes the named construct function registration
    '''
    if name in gConstructs:
        del gConstructs[name]
        return True
    else:
        return False

######################
#EventScripts events #
######################

def es_map_start(event_var):
    '''
event es_map_start is fired when a map is loaded on the server
    '''
    es.loadevents("addons/source-python/plugins/es_emulator/libs/popup/popup.res")
    gUsers.__init__()

def es_client_command(event_var):
    '''
event es_client_command is fired when the user chooses a menu item
    '''
    es.dbgmsg(1,"Popuplib: es_client_command")
    command = event_var['command']
    if command == "menuselect":
        try:
            choice = int(event_var['commandstring'])
            userid = int(event_var['userid'])
            user = gUsers[userid]
            if user.closemode:
                es.dbgmsg(1,"Popuplib: setting closemode to False")
                user.closemode = False
                user.handleQueue()
            else:
                active = user.active
                if active:
                    active.handleChoice(choice, userid)
        except ValueError:
            # It was not a popup menuselect
            pass


# Register for es_map_start to be able to use custom events
es.addons.registerForEvent(selfmodule, 'es_map_start', es_map_start)
# Declare popup events
es.loadevents("declare", "addons/eventscripts/popup/popup.res")

updateGameName()

es_map_start(None)
es.set('_popup_userid',0,'Userid of the current popup user')

########################
# GameThread functions #
########################

def gt_priofinish(user):
    user.prioritized = False

def gt_event_info_check():
    global _allow_event_info
    es.getEventInfo('es_event')
    _allow_event_info = True

#######################
# Built-in constructs #
#######################

def ConstructPlayerList(popupid, flags, menuselectfb):
    '''
    Constructs a playerlist
    '''
    def updatelisting(p):
        playerlist = playerlib.getPlayerList(flags)
        useridlist = [int(x) for x in playerlist]
        if useridlist != p.construct_check:
            p.construct_check = useridlist
            langs = list(p.options.keys())
            mainopt = p.options[p.editlang]
            mainopt.clear()
            for player in playerlist:
                p.addoption(int(player), player.attributes['name'])
            for lang in langs:
                p.options[lang] = mainopt
            return True
        else:
            return False
    thenewmenu = easymenu(popupid, None, menuselectfb)
    thenewmenu.cachemode = "construct"
    thenewmenu.construct = updatelisting
    thenewmenu.construct_check = None
    return thenewmenu


registerConstruct('players', ConstructPlayerList)

_allow_event_info = False
gamethread.delayed(1, gt_event_info_check)
