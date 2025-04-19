import es
import playerlib
import popuplib
import gamethread
import collections.abc

#plugin information
info = es.AddonInfo()
info.name = "Vote EventScripts python library"
info.version = "oy5"
info.author = "Hunter"
info.url = "http://www.eventscripts.com/pages/Vote/"
info.description = "Provides vote handling for Source games"

#global variables:
## gVotes holds all the popups by their names for backwards compatibility
gVotes = {}
## gUsers holds user-specific information such as votes
gUsers = {}
## gVariables holds all ES classic block variables
gVariables = {}
gVariables['vote_name']     = es.ServerVar('_vote_name', '', 'Name of the vote')
gVariables['vote_id']       = es.ServerVar('_vote_id', 0, 'ID of the winning answer')
gVariables['vote_text']     = es.ServerVar('_vote_text', 0, 'Text of the winning answer')
gVariables['vote_count']    = es.ServerVar('_vote_count', 0, 'Votes of the winning answer')
gVariables['vote_percent']  = es.ServerVar('_vote_percent', 0, 'Percentage of the winning answer')
gVariables['vote_votes']    = es.ServerVar('_vote_votes', 0, 'Total votes')
gVariables['vote_tie']      = es.ServerVar('_vote_tie', 0, '1 if there would be two or more winning answers and 0 if there is only one winning answer')
gVariables['vote_canceled'] = es.ServerVar('_vote_canceled', 0, '1 if the vote was canceled and 0 if it was normaly stopped')
gVariables['vote_userid']   = es.ServerVar('_vote_userid', 0, 'UserID that submitted the answer')

## Vote_vote class is the vote base class
class Vote_vote(object):
    def __init__(self, pVoteid, pEndblock = None, pSubblock = None):
        #initialization of vote
        self.name = pVoteid             #vote name for backwards compatibility
        self.running = False            #if the vote is running
        self.votes = 0                  #number of votes
        self.time = 0                   #time remaining
        self.question = ""              #vote question
        self.options = {}               #list of vote options
        self.endblock = pEndblock       #block that runs at the end of vote
        self.subblock = pSubblock       #block that runs for each submitted vote
        self.popup = None               #popup object
        #variables open to the public
        self.showmenu = True            #show the popup (set to False for e.g. HL2DM servers)
        self.endtime = True             #stop vote after the time is over
        self.enduser = True             #stop vote after all users voted
    def delete(self):
        delete(self.name)
    def start(self, time=0):
        if not self.running:
            self.time = time
            self.running = True
            self.votes = 0
            self.popup = popuplib.easymenu("vote_"+str(self.name), "_vote_choice", _submit)
            self.popup.settitle(self.question)
            self.popup.vguititle = self.question.replace('\\n', ' - ')
            for option in self.options:
                self.popup.addoption(option, self.options[option].text)
            if self.showmenu:
                self.send(playerlib.getUseridList("#human"), True, False)
            if self.time > 0:
                gamethread.delayed(1, _ticker, (self.name))
            else:
                self.endtime = False
        else:
            es.dbgmsg(0,"Votelib: Cannot start vote '%s', it is already running"%self.name)
    def stop(self, cancel=None, internal=None):
        if self.running:
            self.popup.unsend(playerlib.getUseridList("#human"))
            self.popup.delete()
            self.popup = None
            if self.endblock:
                if cancel:
                    gVariables['vote_name'].set(self.name)
                    gVariables['vote_id'].set(0)
                    gVariables['vote_text'].set(0)
                    gVariables['vote_count'].set(0)
                    gVariables['vote_percent'].set(0)
                    gVariables['vote_votes'].set(self.votes)
                    gVariables['vote_tie'].set(0)
                    gVariables['vote_canceled'].set(1)
                else:
                    gVariables['vote_name'].set(self.name)
                    gVariables['vote_votes'].set(self.votes)
                    gVariables['vote_canceled'].set(0)
                    gVariables['vote_count'].set(0)
                    for option in self.options: 
                        if int(self.options[option]) > int(gVariables['vote_count']):
                            gVariables['vote_id'].set(option)
                            gVariables['vote_text'].set(self.options[option].getText())
                            gVariables['vote_count'].set(self.options[option].submits)
                            gVariables['vote_tie'].set(0)
                            gVariables['vote_percent'].set(int((self.options[option].submits * 100) / self.votes) if self.votes > 0 else 100)
                        elif int(self.options[option]) == int(gVariables['vote_count']) and int(gVariables['vote_count']) > 0: 
                            gVariables['vote_tie'].set(1)
                if isinstance(self.endblock, collections.abc.Callable):
                    self.endblock(self.name, int(gVariables['vote_id']), str(gVariables['vote_text']), int(gVariables['vote_count']), int(gVariables['vote_percent']), self.votes, True if int(gVariables['vote_tie']) else False, True if cancel else False)
                else:
                    es.doblock(self.endblock)
            self.running = False
            self.votes = 0
            self.time = 0
            for userid in gUsers:
                user = gUsers[userid]
                user.state[self.name] = False
                user.voted[self.name] = None
        else:
            es.dbgmsg(0,"Votelib: Cannot stop vote '%s', it is not running"%self.name)
    def send(self, pUsers, force=False, prio=False):
        try:
            # try if pUsers is just a single userid
            userid = int(pUsers)
            pUsers = [userid]
        except TypeError:
            pass
        if self.running and self.popup and self.showmenu:
            for userid in pUsers:
                if not userid in gUsers:
                    gUsers[userid] = Vote_user(userid)
                if not self.name in gUsers[userid].state:
                    gUsers[userid].state[self.name] = False
                if not gUsers[userid].state[self.name]:
                    self.popup.send(userid, prio)
                    es.dbgmsg(1, "Votelib: Send popup '%s' to user %s"%(self.name, userid))
                elif force:
                    self.popup.send(userid, prio)
                    es.dbgmsg(1, "Votelib: Forced popup '%s' to user %s"%(self.name, userid))
        elif not self.running:
            es.dbgmsg(0,"Votelib: Cannot send vote '%s', it is not running"%self.name)
    def submit(self, pUsers, option, force=False):
        try:
            # try if pUsers is just a single userid
            userid = int(pUsers)
            pUsers = [userid]
        except TypeError:
            pass
        if self.running and self.popup and self.isValidOption(option):
            for userid in pUsers:
                if not userid in gUsers:
                    gUsers[userid] = Vote_user(userid)
                if not self.name in gUsers[userid].state:
                    gUsers[userid].state[self.name] = False
                if not self.name in gUsers[userid].voted:
                    gUsers[userid].voted[self.name] = 0
                if not gUsers[userid].state[self.name]:
                    self.options[option].add()
                    self.votes += 1
                    gUsers[userid].state[self.name] = True
                    gUsers[userid].voted[self.name] = option
                elif force:
                    if gUsers[userid].voted[self.name]:
                        self.options[gUsers[userid].voted[self.name]].sub
                        self.votes -= 1
                    self.options[option].add()
                    self.votes += 1
                    gUsers[userid].state[self.name] = True
                    gUsers[userid].voted[self.name] = option
                if self.subblock and gUsers[userid].voted[self.name] == option:
                    gVariables['vote_name'].set(self.name)
                    gVariables['vote_id'].set(option)
                    gVariables['vote_text'].set(self.options[option].getText())
                    gVariables['vote_userid'].set(userid)
                    if isinstance(self.subblock, collections.abc.Callable):
                        self.subblock(userid, self.name, option, self.options[option].getText())
                    else:
                        es.doblock(self.subblock)
            if self.enduser and self.votes >= len(playerlib.getUseridList("#human")):
                self.endtime = True
                self.time = 1
        elif not self.running:
            es.dbgmsg(0,"Votelib: Cannot submit vote '%s', it is not running"%self.name)
    def information(self, listlevel):
        if listlevel >= 1:
            es.dbgmsg(0, " ")
        es.dbgmsg(0, self.name)
        if listlevel >= 1:
            es.dbgmsg(0, "  Running:      "+str(self.running))
            es.dbgmsg(0, "  Votes:        "+str(self.votes))
            es.dbgmsg(0, "  Timeleft:     "+str(self.time))
            es.dbgmsg(0, "  Question:     "+str(self.question))
            es.dbgmsg(0, "  Endblock:     "+str(self.endblock))
            es.dbgmsg(0, "  Subblock:     "+str(self.subblock))
            es.dbgmsg(0, "  Showmenu:     "+str(self.showmenu))
            es.dbgmsg(0, "  Endtime:      "+str(self.endtime))
            es.dbgmsg(0, "  Enduser:      "+str(self.enduser))
        if listlevel >= 2:
            es.dbgmsg(0, "  Options:      "+str(len(self.options)))
            for option in self.options:
                es.dbgmsg(0,"    ["+str(option)+"]:  "+self.options[option].getText())
    def isValidOption(self, option):      #checks for valid options numbers
        if (option < 1): return False
        if (option > len(self.options) and not new): return False
        return True
    def setquestion(self, text):          #set the question of the vote
        if not self.running:
            self.question = text
        else:
            es.dbgmsg(0,"Votelib: Cannot setquestion vote '%s', it is already running"%self.name)
    def setoption(self, option, text):    #add a line of text to the end of the list
        if not self.running:
            if self.isValidOption(option):
                self.options[option] = Vote_option(text)
            elif option > len(self.options):
                self.addoption(text)
            else:
                es.dbgmsg(0,"Votelib: Cannot modify option #"+str(option)+"("+text+") in "+self.name)
        else:
            es.dbgmsg(0,"Votelib: Cannot setoption vote '%s', it is already running"%self.name)
    def addoption(self, text):            #add a line of text to the end of the list
        if not self.running:
            self.options[len(self.options)+1] = Vote_option(text)
        else:
            es.dbgmsg(0,"Votelib: Cannot addoption vote '%s', it is already running"%self.name)
    def deloption(self, option):          #delete an option
        if not self.running:
            if self.isValidOption(option):
                for thisoption in range(option, len(self.options)):
                    self.options[thisoption] = self.options[thisoption+1]
                del self.options[len(self.options)]
            else:
                es.dbgmsg(0,"Votelib: Cannot delete option #%s, it does not eixsts"%option)
        else:
            es.dbgmsg(0,"Votelib: Cannot deloption vote '%s', it is already running"%self.name)
    def getvotes(self, option=None):
        if option:
            if self.isValidOption(option):
                return int(self.options[option])
            else:
                return None
        else:
            return self.votes
    def gettimeleft(self):
        return self.time

# Vote_option class
class Vote_option(object):
    def __init__(self, text):
        self.text = text
        self.submits = 0
    def __int__(self):
        return self.submits
    def __str__(self):
        return self.text
    def add(self):
        self.submits += 1
    def sub(self):
        self.submits -= 1
    def getText(self):
        try:
            return self.text['en']
        except:
            return self.text

# Vote user class
class Vote_user(object):
    def __init__(self, userid):
        self.userid = userid
        self.state = {}
        self.voted = {}

#vote commands begin here
#usage from other Python scripts for example:
#  import es
#  import vote
#  a = vote.create("insertnamehere")
def create(pVoteid, pEndblock=None, pSubblock=None):
    #create new normal vote
    gVotes[pVoteid] = Vote_vote(pVoteid, pEndblock, pSubblock)
    return gVotes[pVoteid]

def delete(pVoteid):
    #delete a vote
    if (pVoteid in gVotes):
        del gVotes[pVoteid]
    else:
        raise ValueError(f"Votelib: Cannot delete vote {pVoteid}, it does not exists")

def exists(pVoteid):
    #does named vote exist
    return (pVoteid in gVotes)

def isrunning(pVoteid):
    #does named vote exist and is running (started)
    if (pVoteid in gVotes):
        return gVotes[pVoteid].running
    return False

def find(pVoteid):
    #return class instance of named popup
    if (pVoteid in gVotes):
        return gVotes[pVoteid]
    return None

def send(pVoteid, pUserid, force=False, prio=False):
    #send a named vote to user/users
    if pVoteid in gVotes:
        gVotes[pVoteid].send(pUserid,force,prio)
    else:
        raise ValueError(f"Votelib: Cannot send vote {pVoteid}, it does not exists")

def getmenuname(pPopupid):
    if popuplib.exists(pPopupid):
        if pPopupid.startswith('vote_') and exists(pPopupid[5:]):
            return pPopupid[5:]
    return ''

def getvotelist():
    return list(gVotes.keys())

###################
#Helper functions #
###################

def _ticker(vname):
    vote = find(vname)
    if vote and vote.running:
        vote.time -= 1
        if vote.time > 0:
            gamethread.delayed(1, _ticker, (vote.name))
        elif vote.endtime:
            vote.stop(False, True)

def _submit(userid, value, popupid):
    if popuplib.exists(popupid):
        find(getmenuname(popupid)).submit(userid, value, True)

######################
#EventScripts events #
######################

def player_disconnect(event_var):
    #player gone, delete from memory
    if int(event_var['userid']) in gUsers:
        del gUsers[int(event_var['userid'])]

# Register for player events to be able to use custom events
es.addons.registerForEvent(__import__('votelib'), 'player_disconnect', player_disconnect)
