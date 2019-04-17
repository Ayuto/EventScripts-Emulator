import es
import os
import time
import pickle
import keyvalues
import gamethread
import langlib
import playerlib
import popuplib
import keymenulib

#plugin information
info = es.AddonInfo()
info.name = 'Setting EventScripts python library'
info.version = 'oy3b'
info.author = 'Hunter'
info.url = 'http://www.eventscripts.com/pages/Setting/'
info.description = 'Provides user based setting handling for Source games'

#global variables:
## gSettings holds all the settings by their names for backwards compatibility
gSettings = {}

# Get this library handle for registering events dynamically:
selfmodule = __import__('settinglib')
# Get the data path for reading/writing KeyValues
selfdatapath = '%s/%s' % (es.server_var['eventscripts_addondir'], 'setting/data')
selfdatatest = '%s/__init__.pkl' % selfdatapath
# Get the language strings
selflangpath = '%s/%s' % (es.server_var['eventscripts_addondir'], '_libs/python/settinglib')
selflangtext = langlib.Strings(selflangpath + '/strings.ini')
# Create default data folder
if not os.path.isdir(selfdatapath):
    os.mkdir(selfdatapath)
    
## Setting_setting class is the setting base class
class Setting_base(object):
    def __init__(self, pType, pFilename, pFiletype):
        self.filename = pFilename
        self.filetype = pFiletype
        self.popup = {}                 #contains the popup object's per userid
        self.backmenuvar = 0            #backmenu that displays on 0. Cancel
        self.languages = selflangtext   #langlib object
        self.keyvalues = self.createKey(self.name)
        self.init(str(pType))
    def delete(self):
        #delete this setting, calls global delete function
        delete(self.name)
    def clear(self, timestamp=None):
        clearlist = []
        if timestamp:
            timediff = int(time.time()) - int(timestamp)
            for steamid in list(self.keyvalues['users'].keys()):
                if self.keyvalues['users'][steamid]['time'] < timediff:
                    clearlist.append(steamid)
            for steamid in clearlist:
                del self.keyvalues['users'][steamid]
        else:
            self.keyvalues['users'] = self.createKey('users')
        clearlist = []
        for steamid in list(self.keyvalues['variables'].keys()):
            for variable in list(self.keyvalues['variables'][steamid].keys()):
                clearlist.append((steamid, variable))
        for steamid, variable in clearlist:
            del self.keyvalues['variables'][steamid][variable]
        for option in list(self.keyvalues['options'].keys()):
            self.keyvalues['options'][option]['globstate'] = self.keyvalues['options'][option]['state']
    def init(self, type):
        try:
            self.load()
            if not self.name == self.keyvalues['config']['name']: raise ValueError
        except:
            pass
        self.keyvalues['config'] = self.createKey('config')
        self.keyvalues['config']['name'] = self.name
        self.keyvalues['config']['descr'] = self.descr
        self.keyvalues['config']['resend'] = 1
        self.keyvalues['config']['sound'] = None
        self.keyvalues['config']['type'] = type
        self.keyvalues['options'] = self.createKey('options')
        self.keyvalues['users'] = self.createKey('users')
        self.keyvalues['variables'] = self.createKey('variables')
        self.keyvalues['variables']['global'] = self.createKey('global')
        self.save()
    def save(self):
        self.cleanTypes()
        if self.filetype == 'keyvalues':
            self.keyvalues.save(self.filename)
        elif self.filetype == 'dict':
            pickle_file = open(self.filename, 'wb')
            pickle.dump(self.keyvalues, pickle_file)
            pickle_file.flush()
            pickle_file.close()
    def saveToFile(self, filename, overwriteFilename=False):
        #this method is only for advanced users!
        self.cleanTypes()
        if self.filetype == 'keyvalues':
            self.keyvalues.save(filename)
        elif self.filetype == 'dict':
            pickle_file = open(filename, 'wb')
            pickle.dump(self.keyvalues, pickle_file)
            pickle_file.flush()
            pickle_file.close()
        if overwriteFilename:
            self.filename = filename
    def load(self):
        if self.filetype == 'keyvalues':
            self.keyvalues.load(self.filename)
        elif self.filetype == 'dict':
            pickle_file = open(self.filename, 'rb')
            pickle_file.seek(0)
            self.keyvalues = pickle.load(pickle_file)
            pickle_file.close()
        self.cleanTypes()
    def loadFromFile(self, filename, overwriteFilename=False):
        #this method is only for advanced users!
        if self.filetype == 'keyvalues':
            self.keyvalues.load(filename)
        elif self.filetype == 'dict':
            pickle_file = open(filename, 'rb')
            pickle_file.seek(0)
            self.keyvalues = pickle.load(pickle_file)
            pickle_file.close()
        if overwriteFilename:
            self.filename = filename
        self.cleanTypes()
    def cleanTypes(self):
        resend = self.keyvalues['config']['resend']
        if isinstance(resend, str):
            try:
                self.keyvalues['config']['resend'] = int(resend)
            except:
                self.keyvalues['config']['resend'] = 1
        for option in list(self.keyvalues['options'].keys()):
            if 'state' in self.keyvalues['options'][option]:
                state = self.keyvalues['options'][option]['state']
                if isinstance(state, str):
                    try:
                        self.keyvalues['options'][option]['state'] = int(state)
                    except:
                        self.keyvalues['options'][option]['state'] = 0
            if 'globstate' in self.keyvalues['options'][option]:
                state = self.keyvalues['options'][option]['globstate']
                if isinstance(state, str):
                    try:
                        self.keyvalues['options'][option]['globstate'] = int(state)
                    except:
                        self.keyvalues['options'][option]['globstate'] = 0
        for steamid in list(self.keyvalues['users'].keys()):
            if 'time' in self.keyvalues['users'][steamid]:
                state = self.keyvalues['users'][steamid]['time']
                if isinstance(state, str):
                    try:
                        self.keyvalues['users'][steamid]['time'] = int(state)
                    except:
                        self.keyvalues['users'][steamid]['time'] = int(time.time())
            if 'data' in self.keyvalues['users'][steamid]:
                for option in list(self.keyvalues['users'][steamid]['data'].keys()):
                    if 'state' in self.keyvalues['users'][steamid]['data'][option]:
                        state = self.keyvalues['users'][steamid]['data'][option]['state']
                        if isinstance(state, str):
                            try:
                                self.keyvalues['users'][steamid]['data'][option]['state'] = int(state)
                            except:
                                self.keyvalues['users'][steamid]['data'][option]['state'] = 0
    def createKey(self, name):
        if self.filetype == 'keyvalues':
            return keyvalues.KeyValues(name=name)
        elif self.filetype == 'dict':
            return {}
        else:
            return None
    def send(self, pUsers, prio=False, locked=False):
        raise NotImplemented #type specific
    def sendglobal(self, pUsers, prio=False, locked=False):
        raise NotImplemented #type specific
    def menuUserSubmit(self, userid, value):
        raise NotImplemented #type specific
    def menuUserGlobalSubmit(self, userid, value):
        raise NotImplemented #type specific
    def information(self, listlevel):
        if listlevel >= 1:
            es.dbgmsg(0, ' ')
        es.dbgmsg(0, self.name)
        if listlevel >= 1:
            es.dbgmsg(0, '  Description:  '+str(self.keyvalues['config']['descr']))
            es.dbgmsg(0, '  Re-Send:      '+str(self.keyvalues['config']['resend']))
            es.dbgmsg(0, '  Soundfile:    '+str(self.keyvalues['config']['sound']))
        if listlevel >= 2:
            es.dbgmsg(0, '  Players:      '+str(len(list(self.keyvalues['users'].keys()))))
            es.dbgmsg(0, '  Options:      '+str(len(list(self.keyvalues['options'].keys()))))
            for option in list(self.keyvalues['options'].keys()):
                es.dbgmsg(0,'    ['+str(self.keyvalues['options'][option]['keyname'])+']:  '+self.keyvalues['options'][option]['display'])
    def isValidOption(self, option, passthrough=False):      #checks for valid options
        if option in self.keyvalues['options']:
            return option
        for thisoption in list(self.keyvalues['options'].keys()):
            if self.keyvalues['options'][thisoption]['keyname'] == option:
                return thisoption
        return option if passthrough else False
    def initUser(self, userid):
        if es.exists('userid',userid):
            steamid = playerlib.uniqueid(userid, True)
            self.keyvalues['users'][steamid] = self.createKey(steamid)
            self.keyvalues['users'][steamid]['time'] = int(time.time())
            self.keyvalues['users'][steamid]['data'] = self.createKey('data')
            for option in list(self.keyvalues['options'].keys()):
                self.keyvalues['users'][steamid]['data'][option] = self.createKey(option)
                self.keyvalues['users'][steamid]['data'][option]['state'] = self.keyvalues['options'][option]['state']
    def updateTime(self, userid):
        if es.exists('userid',userid):
            steamid = playerlib.uniqueid(userid, True)
            if steamid in self.keyvalues['users']:
                self.keyvalues['users'][steamid]['time'] = int(time.time())
            else:
                self.initUser(userid)
    def menuUserSubmit(self, userid, value):
        raise NotImplemented #type specific
    def menuUserGlobalSubmit(self, userid, value):
        raise NotImplemented #type specific
    def settitle(self, text):             #set the description of the setting (old method name)
        self.setdescription(text)
    def setdescription(self, text):       #set the description of the setting
        self.descr = text
        self.keyvalues['config']['descr'] = text
        self.save()
    def resend(self, resend):
        self.keyvalues['config']['resend'] = int(resend)
        self.save()
    def setoption(self, key, text, state=None):    #edit/add an option
        option = self.isValidOption(key)
        if option:
            self.keyvalues['options'][option]['display'] = text
            self.keyvalues['options'][option]['state'] = 1 if state else 0
            self.save()
        else:
            es.dbgmsg(0,'Settinglib: Cannot modify option %s, it does not exists'%key)
    def addoption(self, key, text, state=None):            #add an option to the end of the list
        option = self.isValidOption(key, True)
        self.keyvalues['options'][option] = self.createKey(option)
        self.keyvalues['options'][option]['keyname'] = key
        self.keyvalues['options'][option]['display'] = text
        self.keyvalues['options'][option]['state'] = 1 if state else 0
        self.keyvalues['options'][option]['globstate'] = 1 if state else 0
        self.save()
    def deloption(self, key):          #delete an option
        option = self.isValidOption(key, True)
        if option in self.keyvalues['options']:
            del self.keyvalues['options'][option]
            for steamid in list(self.keyvalues['users'].keys()):
                del self.keyvalues['users'][steamid]['data'][option]
            self.save()
        else:
            raise IndexError(f'Settinglib: Cannot delete option {key}, it does not exists')
    def setdefault(self):
        raise NotImplemented #type specific
    def get(self):
        raise NotImplemented #type specific
    def set(self):
        raise NotImplemented #type specific
    def clearoption(self):
        optionlist = []
        for option in list(self.keyvalues['options'].keys()):
            optionlist.append(option)
        for option in optionlist:
            self.deloption(option)
    def addsound(self, sound):            #add a sound file
        self.keyvalues['config']['sound'] = sound
        self.save()
    def delsound(self):                   #delete a sound file
        self.keyvalues['config']['sound'] = None
        self.save()
    def setvar(self, variable, value, userid=None):
        if userid:
            if es.exists('userid',userid):
                steamid = playerlib.uniqueid(userid, True)
                if not steamid in self.keyvalues['users']:
                    self.initUser(int(userid))
            else:
                raise IndexError(f'Settinglib: Cannot find userid {userid}, it does not exists')
        else:
            steamid = 'global'
        self.keyvalues['variables'][steamid][variable] = value
        self.save()
    def getvar(self, variable, userid=None):
        if userid:
            if es.exists('userid',userid):
                steamid = playerlib.uniqueid(userid, True)
                if not steamid in self.keyvalues['users']:
                    self.initUser(int(userid))
            else:
                raise IndexError(f'Settinglib: Cannot find userid {userid}, it does not exists')
        else:
            steamid = 'global'
        return self.keyvalues['variables'][steamid][variable]
    def backmenu(self, backmenu):
        if popuplib.exists(backmenu):
            for page in self.popup:
                self.popup[page].submenu(10, backmenu)
            self.backmenuvar = backmenu
            es.dbgmsg(1, f'Settinglib: Set backmenu of {self.name} to popup {self.backmenuvar}')
            return True
        elif keymenulib.exists(backmenu):
            keymenu = keymenulib.find(backmenu)
            for page in self.popup:
                self.popup[page].submenu(10, keymenu.popup.name)
            self.backmenuvar = keymenu.popup.name
            es.dbgmsg(1, 'Settinglib: Set backmenu of %s to keymenu %s' % (self.name, self.backmenuvar))
            return True
        else:
            es.dbgmsg(0, 'setting: Could not set backmenu of %s to %s' % (self.name, backmenu))
            return False

# Import the used sub-classes
import settinglib.list
import settinglib.toggle

#setting commands begin here
#usage from other Python scripts for example:
#  import es
#  import setting
#  a = setting.create('insertnamehere', 'My Setting', 'list')
def create(pSettingid, pDescription, pType='list', pFilename=None, pFiletype='dict'):
    #check for pickle problems
    if pFiletype == 'dict':
        try:
            pickle_data = list(map(str, list(range(1, 10))))
            pickle_file = open(selfdatatest, 'wb')
            pickle.dump(pickle_data, pickle_file)
            pickle_file.flush()
            pickle_file.close()
            pickle_file = open(selfdatatest, 'rb')
            pickle_file.seek(0)
            pickle_test = pickle.load(pickle_file)
            pickle_file.close()
            os.remove(selfdatatest)
            if pickle_test != pickle_data:
                pFiletype = 'keyvalues'
        except:
            pFiletype = 'keyvalues'
    else:
        pFiletype = 'keyvalues'
    if not pFilename:
        if pFiletype == 'keyvalues':
            pFilename = '%s/%s.txt' % (selfdatapath, pSettingid)
        elif pFiletype == 'dict':
            pFilename = '%s/%s.pkl' % (selfdatapath, pSettingid)
    #create new setting
    if pType == 'list':
        gSettings[pSettingid] = list.Setting_list(pSettingid, pDescription, pFilename, pFiletype)
    elif pType == 'toggle':
        gSettings[pSettingid] = toggle.Setting_toggle(pSettingid, pDescription, pFilename, pFiletype)
    else:
        return None
    return gSettings[pSettingid]
    
def free(pSettingid):
    #free a setting
    if (pSettingid in gSettings):
        if os.path.exists(gSettings[pSettingid].filename):
            os.remove(gSettings[pSettingid].filename)
        del gSettings[pSettingid]
    else:
        raise ValueError(f'Settinglib: Cannot free setting {pSettingid}, it does not exists')

def delete(pSettingid):
    #delete a setting
    if (pSettingid in gSettings):
        del gSettings[pSettingid]
    else:
        raise ValueError(f'Settinglib: Cannot delete setting {pSettingid}, it does not exists')

def exists(pSettingid):
    #does named setting exist
    return (pSettingid in gSettings)

def find(pSettingid):
    #return class instance of named popup
    if (pSettingid in gSettings):
        return gSettings[pSettingid]
    return None

def send(pSettingid, pUserid, prio=False):
    #send a named setting to user/users
    if pSettingid in gSettings:
        gSettings[pSettingid].send(pUserid,prio)
    else:
        raise ValueError(f'Settinglib: Cannot send setting {pSettingid}, it does not exists')

def sendGlobal(pSettingid, pUserid, prio=False):
    #send a named setting to user/users
    if pSettingid in gSettings:
        gSettings[pSettingid].sendGlobal(pUserid,prio)
    else:
        raise ValueError(f'Settinglib: Cannot send setting {pSettingid}, it does not exists')

###################
#Helper functions #
###################

def _submit(userid, value, popupid):
    es.dbgmsg(1, 'Settinglib: _submit(%s, %s, %s)' % (userid, value, popupid))
    page = popuplib.find(popupid)
    if page:
        if page.settingid in gSettings:
            gSettings[page.settingid].menuUserSubmit(userid, value)
        else:
            raise ValueError(f'Settinglib: Invalid setting {page.settingid} submitted from popup')

def _submitGlobal(userid, value, popupid):
    es.dbgmsg(1, 'Settinglib: _submitGlobal(%s, %s, %s)' % (userid, value, popupid))
    page = popuplib.find(popupid)
    if page:
        if page.settingid in gSettings:
            gSettings[page.settingid].menuUserGlobalSubmit(userid, value)
        else:
            raise ValueError(f'Settinglib: Invalid setting {page.settingid} submitted from popup')
        

def _saveTicker():
    gamethread.delayed(300, _saveTicker, ())
    for setting in gSettings:
        gSettings[setting].save()
        
def _saveAll():
    for setting in gSettings:
        gSettings[setting].save()
                    
######################
#EventScripts events #
######################

def es_map_start(event_var):
    gamethread.delayed(300, _saveTicker, ())    

def player_activate(event_var):
    userid = int(event_var['userid'])
    steamid = playerlib.uniqueid(userid, True)
    for setting in gSettings:
        if not steamid in gSettings[setting].keyvalues['users']:
            gSettings[setting].initUser(userid)
        gSettings[setting].updateTime(userid)

# Register for custom events
es.addons.registerForEvent(selfmodule, 'es_map_start', es_map_start)
es.addons.registerForEvent(selfmodule, 'player_activate', player_activate)
