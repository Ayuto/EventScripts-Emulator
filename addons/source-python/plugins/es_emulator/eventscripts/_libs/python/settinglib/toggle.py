import settinglib
from settinglib import Setting_base

import es
import os
import time
import playerlib
import popuplib

## Setting_setting class is the setting base class
class Setting_toggle(Setting_base):
    def __init__(self, pSettingid, pDescription, pFilename, pFiletype):
        #initialization of setting
        self.name = pSettingid          #setting name for backwards compatibility
        self.descr = pDescription       #description
        Setting_base.__init__(self, 'toggle', pFilename, pFiletype)
    def send(self, pUsers, prio=False, locked=False):
        try:
            # try if pUsers is just a single userid
            userid = int(pUsers)
            pUsers = [userid]
        except TypeError:
            pass
        if locked:
            optionstate = 0
        else:
            optionstate = 1
        for userid in pUsers:
            player = playerlib.getPlayer(userid)
            if player:
                steamid = playerlib.uniqueid(userid, True)
                menuname = '_setting_%s_user%s' % (self.name, userid)
                helpline = self.languages('setting '+self.keyvalues['config']['type']+' help', (), player.get('lang'))
                if not popuplib.active(userid)['name'] == menuname and not popuplib.isqueued(menuname, userid) or prio:
                    self.popup[userid] = popuplib.easymenu(menuname, '_setting_choice', settinglib._submit)
                    self.popup[userid].settingid = self.name
                    self.popup[userid].c_titleformat = self.keyvalues['config']['descr'] + (' '*(30-len(self.keyvalues['config']['descr']))) + ' (%p/%t)\n' + helpline
                    if not steamid in self.keyvalues['users']:
                        self.initUser(userid)
                    for option in list(self.keyvalues['options'].keys()):
                        display = self.keyvalues['options'][option]['display']
                        userdata = self.keyvalues['users'][steamid]['data']
                        if option in userdata:
                            if userdata[option]['state']:
                                active = self.languages('setting toggle on', (), player.get('lang'))
                                self.popup[userid].addoption(option, display + ' ('+active+')', optionstate)
                                continue
                        active = self.languages('setting toggle off', (), player.get('lang'))
                        self.popup[userid].addoption(option, display + ' ('+active+')', optionstate)
                    if self.backmenuvar:
                        self.popup[userid].submenu(10, self.backmenuvar)
                    self.popup[userid].send(userid, prio)
    def sendglobal(self, pUsers, prio=False, locked=False):
        try:
            # try if pUsers is just a single userid
            userid = int(pUsers)
            pUsers = [userid]
        except TypeError:
            pass
        if locked:
            optionstate = 0
        else:
            optionstate = 1
        for userid in pUsers:
            player = playerlib.getPlayer(userid)
            if player:
                menuname = '_setting_%s_user%s_global' % (self.name, userid)
                helpline = self.languages('setting '+self.keyvalues['config']['type']+' help', (), player.get('lang'))
                if not popuplib.active(userid)['name'] == menuname and not popuplib.isqueued(menuname, userid) or prio:
                    self.popup['global'] = popuplib.easymenu(menuname, '_setting_choice', settinglib._submitGlobal)
                    self.popup['global'].settingid = self.name
                    self.popup['global'].c_titleformat = self.keyvalues['config']['descr'] + (' '*(30-len(self.keyvalues['config']['descr']))) + ' (%p/%t)\n' + helpline
                    for option in list(self.keyvalues['options'].keys()):
                        display = self.keyvalues['options'][option]['display']
                        userdata = self.keyvalues['options']
                        if option in userdata:
                            if userdata[option]['globstate']:
                                active = self.languages('setting toggle on', (), player.get('lang'))
                                self.popup['global'].addoption(option, display + ' ('+active+')', optionstate)
                                continue
                        active = self.languages('setting toggle off', (), player.get('lang'))
                        self.popup['global'].addoption(option, display + ' ('+active+')', optionstate)
                    if self.backmenuvar:
                        self.popup['global'].submenu(10, self.backmenuvar)
                    self.popup['global'].send(userid, prio)
    def menuUserSubmit(self, userid, value):
        if es.exists('userid',userid):
            self.toggle(value, userid)
            if self.keyvalues['config']['sound']:
                es.playsound(userid, self.keyvalues['config']['sound'], 1.0)
            if self.keyvalues['config']['resend']:
                self.send(userid, True)
    def menuUserGlobalSubmit(self, userid, value):
        if es.exists('userid',userid):
            self.toggle(value)
            if self.keyvalues['config']['sound']:
                es.playsound(userid, self.keyvalues['config']['sound'], 1.0)
            if self.keyvalues['config']['resend']:
                self.sendglobal(userid, True)
    def setdefault(self, key, state=None, overwrite=None):
        option = self.isValidOption(key)
        if option:
            self.keyvalues['options'][option]['state'] = 1 if state else 0
            if overwrite:
                for steamid in list(self.keyvalues['users'].keys()):
                    self.keyvalues['users'][steamid]['data'][option]['state'] = 1 if state else 0
        else:
            raise IndexError(f'Settinglib: Cannot set option {key} as default, it does not exists')
    def set(self, key, state=None, userid=None):
        option = self.isValidOption(key)
        if option:
            if userid:
                steamid = playerlib.uniqueid(userid, True)
                if steamid:
                    if not steamid in self.keyvalues['users']:
                        self.initUser(int(userid))
                    self.keyvalues['users'][steamid]['data'][option]['state'] = 1 if state else 0
                else:
                    raise IndexError(f'Settinglib: Cannot find userid {userid}')
            else:
                self.keyvalues['options'][option]['globstate'] = 1 if state else 0
        else:
            raise IndexError(f'Settinglib: Cannot set option {key}, it does not exists')
    def get(self, key, userid=None):
        option = self.isValidOption(key)
        if option:
            if userid:
                steamid = playerlib.uniqueid(userid, True)
                if steamid:
                    if not steamid in self.keyvalues['users']:
                        self.initUser(int(userid))
                    try:
                        return bool(self.keyvalues['users'][steamid]['data'][option]['state'])
                    except KeyError:
                        return bool(self.keyvalues['options'][option]['state'])
                else:
                    raise IndexError(f'Settinglib: Cannot find userid {userid}')
            else:
                return bool(self.keyvalues['options'][option]['globstate'])
        else:
            raise IndexError(f'Settinglib: Cannot get option {key}, it does not exists')
    def toggle(self, key, userid=None):
        option = self.isValidOption(key)
        if option:
            self.set(option, not(self.get(option, userid)), userid)
        else:
            raise IndexError(f'Settinglib: Cannot toggle option {key}, it does not exists')
