import es
import keyvalues
import settinglib
import playerlib
import popuplib
import collections

#plugin information
info = es.AddonInfo()
info.name = "Keymenu EventScripts python library"
info.version = "0.9"
info.author = "Hunter"
info.url = "http://www.eventscripts.com/pages/Keymenu/"
info.description = "Provides menu and pop-up creation from keygroups"

#global variables:
## gKeymenus holds all the keymenus by their names for backwards compatibility
gKeymenus = {}

# Keymenu_keymenu is the normal keymenu class
class Keymenu_keymenu(object):
    def __init__(self, gKeymenuid, returnvar, block, keygroup, menudisplay, menureturn, titletext, update = None, backpopup = None):
        #initialization of keymenu
        self.name = gKeymenuid          #keymenu name for backwards compatibility
        self.keygroup = keygroup        #keygroup that is used to create the menu
        self.block = block              #block/function that executes on menuselect
        self.returnvar = returnvar      #variable that contains the menu-return
        self.titletext = titletext      #title of the keymenu
        self.menudisplay = menudisplay  #indicator for the display key or keyvalue
        self.menureturn = menureturn    #indicator for the return key or keyvalue
        self.popup = None               #contains the popup object
        self.backpopup = backpopup      #contains the back popup object
        self.keyvalues = None           #contains the keyvalues object
        self.pagecount = 0              #number of pages
        self.linecount = 0              #number of options in the menu
        #create the popup object
        if es.exists("keygroup", self.keygroup) or isinstance(self.keygroup, keyvalues.KeyValues):
            if "#" in self.menudisplay and "#" in self.menureturn:
                self.menudisplay = self.menudisplay.split(" ")
                self.menureturn = self.menureturn.split(" ")
                if not len(self.menudisplay) > 1:
                    self.menudisplay.append('')
                if not len(self.menureturn) > 1:
                    self.menureturn.append('')
                if len(self.titletext) > 0:
                    self.popup = popuplib.easymenu("keymenu_"+str(self.name), self.returnvar, _keymenu_select)
                    self.popup.settitle(self.titletext)
                    self.popup.vguititle = self.titletext.replace('\\n', ' - ')
                    if not isinstance(self.keygroup, keyvalues.KeyValues):
                        self.keyvalues = keyvalues.getKeyGroup(self.keygroup)
                    else:
                        self.keyvalues = self.keygroup
                        self.keygroup = self.keyvalues.getName()
                    if self.menudisplay[0] == "#key" and self.menureturn[0] == "#key":
                        for key in list(self.keyvalues.keys()):
                            self.popup.addoption(key, key)
                            self.linecount += 1
                    elif self.menudisplay[0] == "#key" and self.menureturn[0] == "#keyvalue":
                        for key in list(self.keyvalues.keys()):
                            self.popup.addoption(self.keyvalues[key][self.menureturn[1]], key)
                            self.linecount += 1
                    elif self.menudisplay[0] == "#keyvalue" and self.menureturn[0] == "#key":
                        for key in list(self.keyvalues.keys()):
                            self.popup.addoption(key, self.keyvalues[key][self.menudisplay[1]])
                            self.linecount += 1
                    elif self.menudisplay[0] == "#keyvalue" and self.menureturn[0] == "#keyvalue":
                        for key in list(self.keyvalues.keys()):
                            self.popup.addoption(self.keyvalues[key][self.menureturn[1]], self.keyvalues[key][self.menudisplay[1]])
                            self.linecount += 1
                    if self.linecount:
                        self.popup.checklang('en')
                    else:
                        self.popup.delete()
                        self.popup = None
                        self.keyvalues = None
                        raise ValueError(f"Keymenulib: No keys or keyvalues found in {keygroup}")
                else:
                    raise ArgumentError("Keymenulib: No titletext")
            else:
                raise ArgumentError("Keymenulib: No #key or #keyvalue found in the commandstring")
        else:
            raise ValueError(f"Keymenulib: The keygroup {keygroup} does not exists")
    def delete(self):
        delete(self.name)
    def changeblock(self, block):
        self.block = block
    def information(self, listlevel):
        es.dbgmsg(0, self.name)
        if listlevel >= 1:
            es.dbgmsg(0, "  Keygroup:     "+str(self.keygroup))
            es.dbgmsg(0, "  Block:        "+str(self.block))
            es.dbgmsg(0, "  Variable:     "+str(self.returnvar))
            es.dbgmsg(0, "  Titletext:    "+str(self.titletext))
            es.dbgmsg(0, "  Menudisplay:  "+' '.join(self.menudisplay))
            es.dbgmsg(0, "  Menureturn:   "+' '.join(self.menureturn))
            es.dbgmsg(0, "  Backpopup:    "+str(self.backpopup))
            es.dbgmsg(0, "  Linecount:    "+str(self.linecount))
            es.dbgmsg(0, "  Pagecount:    "+str(self.getpages()))
            es.dbgmsg(0, " ")
    def send(self, pUsers, pPage=None):
        if self.popup:
            if pPage:
                self.popup.sendPage(pUsers, pPage)
            else:
                self.popup.send(pUsers)
            es.dbgmsg(1, f"Keymenulib: Send keymenu '{self.name}' to users '{pUsers}'")
        else:
            es.dbgmsg(0, f"keymenu: Could not send keymenu '{self.name}', the popup object was not created!")
    def unsend(self, pUsers, pPage=None):
        if self.popup:
            if pPage:
                self.popup.unsendPage(pUsers, pPage)
            else:
                self.popup.unsend(pUsers)
            es.dbgmsg(1, f"Keymenulib: Unsend keymenu '{self.name}' from users '{pUsers}'"))
        else:
            es.dbgmsg(0, f"keymenu: Could not unsend keymenu '{self.name}', the popup object was not created!")
    def update(self, keygroup = None):
        if keygroup:
            self.keygroup = keygroup
        self.__init__(self.name, self.returnvar, self.block, self.keygroup, ' '.join(self.menudisplay), ' '.join(self.menureturn), self.titletext, True, self.backpopup)
    def getpages(self):
        if self.popup:
            self.pagecount = self.popup.getPageCount()
        else:
            es.dbgmsg(0, f"keymenu: Could not get pagecount of keymenu '{self.name}', the popup object was not created!")
        return self.pagecount
    def backmenu(self, backmenu):
        if popuplib.exists(backmenu):
            self.popup.submenu(10, popuplib.find(backmenu))
            self.backpopup = popuplib.find(backmenu)
            es.dbgmsg(1, f"Keymenulib: Set backmenu of '{self.name}' to popup '{self.backpopup}'")
            return True
        elif settinglib.exists(backmenu):
            self.popup.submenu(10, settinglib.find(backmenu).popup)
            self.backpopup = settinglib.find(backmenu).popup
            es.dbgmsg(1, f"Keymenulib: Set backmenu of '{self.name}' to setting '{self.backpopup}'")
            return True
        elif exists(backmenu):
            self.popup.submenu(10, find(backmenu).popup)
            self.backpopup = find(backmenu).popup
            es.dbgmsg(1, f"Keymenulib: Set backmenu of '{self.name}' to keymenu '{self.backpopup}'")
            return True
        else:
            es.dbgmsg(0, f"keymenu: Could not set backmenu of '{self.name}' to '{backmenu}'!")
            return False

#keymenu commands begin here
#usage from other Python scripts for example:
#  import es
#  import keymenu
#  from keymenu import keymenu
#  es.server.cmd("es_xcreateplayerlist playerlist")
#  a = keymenu.create("insertnamehere", "_keymenu_select", "myscript/myblock", "playerlist", "#keyvalue name", "#key", "Playerlist\nSelect a player")
#  a.send(es.getuserid("Hunter"))
#  a.delete
def create(pKeymenuid, returnvar, block, keygroup, menudisplay, menureturn, titletext):
    gKeymenus[pKeymenuid] = Keymenu_keymenu(pKeymenuid, returnvar, block, keygroup, menudisplay, menureturn, titletext)
    return gKeymenus[pKeymenuid]

def delete(pKeymenuid):
    if pKeymenuid in gKeymenus:
        k = gKeymenus[pKeymenuid]
        k.popup.unsend(es.getUseridList())
        k.popup.delete()
        del gKeymenus[pKeymenuid]
    else:
        raise ValueError(f"Keymenulib: Cannot delete keymenu {pKeymenuid}, it does not exist")

def exists(pKeymenuid):
    return (pKeymenuid in gKeymenus)

def find(pKeymenuid):
    if pKeymenuid in gKeymenus:
        return gKeymenus[pKeymenuid]
    return None

def send(pKeymenuid, pUserid, pPage=None):
    if pKeymenuid in gKeymenus:
        gKeymenus[pKeymenuid].send(int(pUserid), pPage)
    else:
        raise ValueError(f"Keymenulib: Cannot send keymenu {pKeymenuid}, it does not exist")

def unsend(pKeymenuid, pUserid, pPage=None):
    if pKeymenuid in gKeymenus:
        gKeymenus[pKeymenuid].unsend(int(pUserid), pPage)
    else:
        raise ValueError(f"Keymenulib: Cannot unsend keymenu {pKeymenuid}, it does not exist")
    
def getmenuname(pPopupid):
    if popuplib.exists(pPopupid):
        if pPopupid.startswith('keymenu_') and exists(pPopupid[8:]):
            return pPopupid[8:]
    return ''

def getmenulist():
    return list(gKeymenus.keys())

###################
#Helper functions #
###################

def _keymenu_select(userid, choice, popupid):
    # handling selected option popup/keymenu
    if popuplib.exists(popupid):
        k = find(getmenuname(popupid))
        if k.block:
            if isinstance(k.block, collections.Callable):
                k.block(userid, choice, k.name)
            else:
                es.doblock(k.block)
