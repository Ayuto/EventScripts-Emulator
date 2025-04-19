# ==============================================================================
#   IMPORTS
# ==============================================================================
import es
import gamethread

import collections.abc


# ==============================================================================
#   LIBRARY INFORMATION
# ==============================================================================
info = es.AddonInfo() 
info.name     = "Repeat - EventScripts python library" 
info.version  = "oy4b" 
info.url      = "http://www.eventscripts.com/pages/Repeat/" 
info.basename = "repeat" 
info.author   = "SumGuy14 (Aka SoccerDude) & XE_ManUp"

# ==============================================================================
#   GLOBAL DICTIONARIES AND STATUS CONSTANTS
# ==============================================================================
dict_repeatInfo = {}

STATUS_NOEXIST = 0
STATUS_STOPPED = 1
STATUS_RUNNING = 2
STATUS_STARTED = 3

# ==============================================================================
#   ERROR CLASS
# ==============================================================================
class RepeatError(Exception):
    pass

    
# ==============================================================================
#   REPEAT CLASS
# ==============================================================================
class Repeat:
    def __init__(self, repeatName, command, commandArgs=(), kw=None):
        self.name = str(repeatName)
        
        # Make sure commandArgs is a tuple
        if not isinstance(commandArgs, tuple):
            commandArgs = (commandArgs, )
            
        self.attributes =   {
                                'name':self.name,           # name
                                'interval':0,               # interval
                                'limit':0,                  # limit
                                'time':0,                   # time
                                'timeleft':0,               # timeleft
                                'count':0,                  # count
                                'remaining':0,              # remaining
                                'command':command,          # command
                                'args':commandArgs,         # args
                                'status':STATUS_STOPPED,    # status
                                'keyword':kw or {}          # keyword
                            }
                            
    def __getitem__(self, item):
        # We will be nice and convert the "item" to a lower-cased string
        item = str(item).lower()
        
        # Let's make sure that the item that they are trying to change exists
        if item in self.attributes:
            # Allowing the retrieving of attributes in the dictionary
            return self.attributes[item]
            
    def __setitem__(self, item, value):
        # We will be nice and convert the "item" to a lower-cased string
        item = str(item).lower()
        
        self.attributes[item] = value
            
    def start(self, interval, limit):
        start(self.name, interval, limit)
        
    def stop(self):
        stop(self.name)
        
    def delete(self):
        delete(self.name)
        
    def pause(self):
        pause(self.name)
        
    def resume(self):
        resume(self.name)
        
    def status(self):
        return self.attributes['status']
        
    def info(self, infoType):
        if infoType:
            if infoType in self.attributes:
                return self.attributes[infoType]
            else:
                es.dbgmsg(0, '[repeat] Invalid information type \"%s\" for info command!' %infoType)
                es.dbgmsg(0, '[repeat] Available Types:')
                for attributeName in self.attributes:
                    es.dbgmsg(0, '[repeat]    * %s' %attributeName)
                return None
        
# ==============================================================================
#   DIRECT REPEAT METHODS
# ==============================================================================
def create(repeatName, command, commandArgs=(), kw=None):
    '''
    Creates a repeatable command to be started at any given time.
    Args can be passed in as a tuple, or as keyword argments.
    '''
    # Convert to string
    repeatName = str(repeatName)
    
    # Make sure the repeat exists
    if (repeatName in dict_repeatInfo):
        dict_repeatInfo[repeatName].__init__(repeatName, command, commandArgs, kw)
    else:
        dict_repeatInfo[repeatName] = Repeat(repeatName, command, commandArgs, kw)
        
    return dict_repeatInfo[repeatName]
    
def start(repeatName, interval, limit):
    '''
    Starts the repeatable command and repeats for "limit" times
    every "interval" seconds. If "limit" is 0, the repeat will
    continue to loop indefinately, or until stopped.
    '''
    # Convert to string
    repeatName = str(repeatName)
    
    # Make sure the repeat exists
    if (repeatName in dict_repeatInfo):
        # If the repeat is currently running, stop the repeat
        if dict_repeatInfo[repeatName]['status'] == STATUS_RUNNING:
            stop(repeatName)
            
        # If the repeat is currently stopped or paused, start the repeat
        if dict_repeatInfo[repeatName]['status'] == STATUS_STOPPED or dict_repeatInfo[repeatName]['status'] == STATUS_STARTED:
            # Convert interval to a float
            interval = float(interval)
            
            # Set up initial repeat starting values
            dict_repeatInfo[repeatName]['interval']     = float(interval)
            dict_repeatInfo[repeatName]['limit']        = int(limit)
            dict_repeatInfo[repeatName]['time']         = float(interval) * float(limit)
            dict_repeatInfo[repeatName]['timeleft']     = float(interval) * float(limit)
            dict_repeatInfo[repeatName]['count']        = 0
            dict_repeatInfo[repeatName]['remaining']    = int(limit)
            dict_repeatInfo[repeatName]['status']       = STATUS_RUNNING
            
            # Begin execution of the repeat
            fire(repeatName)
    else:
        raise RepeatError(f'Cannot start repeat: \"{repeatName}\" does not exist.')
        
def stop(repeatName):
    # Convert to string
    repeatName = str(repeatName)
    
    # Make sure the repeat exists
    if (repeatName in dict_repeatInfo):
        # Cancel the delay
        gamethread.cancelDelayed(repeatName)
        
        # Set the repeat status to stopped
        dict_repeatInfo[repeatName]['status'] = STATUS_STOPPED
    else:
        raise RepeatError(f'Cannot stop repeat: \"{repeatName}\" does not exist.')
        
def resume(repeatName):
    # Convert to string
    repeatName = str(repeatName)
    
    # Make sure the repeat exists
    if (repeatName in dict_repeatInfo):
        # If the repeat is already running, do nothing
        if dict_repeatInfo[repeatName]['status'] == STATUS_RUNNING:
            return
            
        # Make sure that we can resume the repeat 
        if ((dict_repeatInfo[repeatName]['interval'] != 0 and dict_repeatInfo[repeatName]['remaining'] > 0) or
            dict_repeatInfo[repeatName]['interval'] == 0):
            
            # Set the status to "running"
            dict_repeatInfo[repeatName]['status'] = STATUS_RUNNING
            
            # Begin the execution of repeat
            fire(repeatName) 
    else:
        raise RepeatError(f'Cannot resume repeat: \"{repeatName}\" does not exist.')
            
def pause(repeatName):
    # Convert to string
    repeatName = str(repeatName)
    
    # Make sure the repeat exists
    if (repeatName in dict_repeatInfo):
        # If the repeat is already running, do nothing
        if dict_repeatInfo[repeatName]['status'] != STATUS_RUNNING:
            return
            
        # Set the status to "paused"
        dict_repeatInfo[repeatName]['status'] = STATUS_STARTED
        
        # Cancel the delay
        gamethread.cancelDelayed(repeatName)
    else:
        raise RepeatError(f'Cannot pause repeat: \"{repeatName}\" does not exist.')
        
def delete(repeatName):
    # Convert to string
    repeatName = str(repeatName)
    
    # Make sure the repeat exists
    if (repeatName in dict_repeatInfo):
        if status(repeatName) == STATUS_RUNNING:
            stop(repeatName)
        del dict_repeatInfo[repeatName]
    else:
        raise RepeatError(f'Cannot delete repeat: \"{repeatName}\" does not exist.')

def status(repeatName):
    # Convert to string
    repeatName = str(repeatName)
    
    # Make sure the repeat exists
    if (repeatName in dict_repeatInfo):
        return dict_repeatInfo[repeatName]['status']
    else:
        return STATUS_NOEXIST

def find(repeatName):
    # Convert to string
    repeatName = str(repeatName)
    
    # Make sure the repeat exists
    if (repeatName in dict_repeatInfo):
        # Return the instance
        return dict_repeatInfo[repeatName]
    else:
        return None

def fire(repeatName):
    # Convert to string
    repeatName = str(repeatName)
    
    # Make sure the repeat exists
    if (repeatName in dict_repeatInfo):
        if dict_repeatInfo[repeatName]['count'] < dict_repeatInfo[repeatName]['limit'] or dict_repeatInfo[repeatName]['limit'] == 0: # make sure the amount of times fired is under its limit
            # Cache list information for readability and slight speed improvements
            interval = dict_repeatInfo[repeatName]['interval']
            command = dict_repeatInfo[repeatName]['command']
            dict_repeatInfo[repeatName]['count'] += 1
            dict_repeatInfo[repeatName]['remaining'] -= 1
            dict_repeatInfo[repeatName]['timeleft'] = dict_repeatInfo[repeatName]['remaining'] * dict_repeatInfo[repeatName]['interval']
            
            if isinstance(command, collections.abc.Callable):
                # Backwards-compatibility check (is the an extra parameter in the method being called?)
                if (len(dict_repeatInfo[repeatName]['args']) + 1 == command.__code__.co_argcount) and "self" not in command.__code__.co_varnames:
                    # Add the repeat instance to the end of the parameter list
                    args = dict_repeatInfo[repeatName]['args'] + (dict_repeatInfo[repeatName], )
                    gamethread.delayedname(interval, repeatName, command, args, dict_repeatInfo[repeatName]['keyword'])
                else:
                    gamethread.delayedname(interval, repeatName, command, dict_repeatInfo[repeatName]['args'], dict_repeatInfo[repeatName]['keyword'])
            else:
                gamethread.delayedname(interval, repeatName, es.server.queuecmd, command)
                
            # Re-fire the fire() loop
            gamethread.delayedname(interval, repeatName, fire, (repeatName))
        else:
            stop(repeatName)
    else:
        raise RepeatError(f'Cannot fire repeat: \"{repeatName}\" does not exist.')
            
def info(repeatName, infoType):
    # Convert to string
    repeatName = str(repeatName)
    
    # Make sure the repeat exists
    if (repeatName in dict_repeatInfo):
        if infoType in list(dict_repeatInfo[repeatName].keys()):
            return dict_repeatInfo[repeatName][infoType]
        else:
            es.dbgmsg(0, '[repeat] Invalid information type \"%s\" for info command!' %infoType)
            es.dbgmsg(0, '[repeat] Available Types:')
            for attributeName in self.attributes:
                es.dbgmsg(0, '[repeat]    * %s' %attributeName)
    else:
        raise RepeatError(f'Cannot retrieve repeat info: \"{repeatName}\" does not exist.')