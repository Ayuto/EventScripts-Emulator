# Copyright 2010, EventScripts Development Team
#   Prototyped by freddukes, updated by Mattie and the team.

import urllib2

import es
import cmdlib
import os

HOST = "http://api.eventscripts.com/updatecheck/"

description = "Controls whether EventScripts will automatically check for updates" 
checkForUpdates = es.ServerVar("eventscripts_checkforupdates", 1, description)
update_notice = es.ServerVar("eventscripts_lastupdatenotice", "unchecked", 
            "Last status text returned when checking for eventscripts updates.")

class Connection(object):
    """
    This object will manage a connection to a specific URL. This will allow us
    to make calls to a web address and return the output of the given address.
    We shall use this to make calls to the ESAM manager which will check for
    updates to the corelib / ES versions. 
    """
    DISCONNECTED = 0
    CONNECTED = 1
    
    UNCACHED = 2
    CACHED = 4
    
    def __init__(self, url):
        """
        Executed when this object is created. Intialise all objects needed and
        assign default values.
        
        @param str url The url that this connection object represents
        """
        self.status = self.__class__.DISCONNECTED
        self.connection = None
        self.url = url
        self.data = None
        self.cached = self.__class__.UNCACHED
        self.cachedUpdateSource = None
                
    def __del__(self):
        """
        Default destructor, executed when this object is destroyed. If there are
        any outstanding connections, we need to destory them so they arent' left
        open in memory.
        """
        self.disconnect()
        
    def connect(self):
        """
        Executed when we want to connect to an object. Return a urllib2
        connection object, or None if the connection was unsuccessful.
        """
        if self.status == self.__class__.CONNECTED:
            return self.connection
        try:
            if self.data is not None:
                formattedData = ""
                for key, value in self.data.iteritems():
                    formattedData += "%s=%s&" % (key, value)
                formattedData = formattedData[:-1]
                self.connection = urllib2.urlopen(self.url, formattedData)
            else:
                self.connection = urllib2.urlopen(self.url)
            self.status = self.__class__.CONNECTED
            return self.connection
        except Exception, e:
            # An error occured, pass it to debug message to be logged.
            error = "[EventScripts] ERROR: Cannot retrieve data from the url: %s"
            es.dbgmsg(1, error % self.url)
            es.dbgmsg(1, str(e))
            update_notice.set(error % self.url)
            return None
        
        
                           
    def disconnect(self):
        """
        Executed when we wish to disconnect the current connection. This will
        run silently if there are no open connections to avoid errors.
        """
        if self.status == self.__class__.CONNECTED:
            self.connection.close()
            self.status = self.__class__.DISCONNECTED
            self.connection = None
            
    def reCacheUpdate(self):
        """
        Recaches the updates (basically checks for a further update and stores
        the result). This requires that we have an open connection.
        """
        if self.status == self.__class__.CONNECTED:
            self.cachedUpdateSource = self.connection.read()
            if not self.cachedUpdateSource:
                # This checks for blank strings and assigns NoneType
                self.cachedUpdateSource = None
            else:
                self.cachedUpdateSource = self.cachedUpdateSource.strip()
                # write to the server variable, too
                update_notice.set(self.cachedUpdateSource)
            self.cached = self.__class__.CACHED
                
    def hasCache(self):
        """
        Returns whether or not this object has been cached (site previously
        queried) this time the server has been executed.
        
        @return bool Whether or not a cache is found
        """
        return bool(self.cached == self.__class__.CACHED) 
        
    def getCache(self):
        """
        Returns the cache results of the previously queried results.
        
        @return str|None The cache results (None if no cache found)
        """
        if self.hasCache():
            return self.cachedUpdateSource
        return None
       
connection = Connection(HOST)

def load():
    """
    Executed when this file is loaded. Create any console commands that we need
    throughout the script.
    """
    cmdlib.registerServerCommand("es_checkversion", checkUpdateCommand,
                                 "Check for any later EventScripts updates")
    es.set()
                                 
def unload():
    """
    Executed when this file is unloaded. Ensure that we clear up any
    dependencies.
    """
    cmdlib.unregisterServerCommand("es_checkversion")
        
def es_map_start(event_var):
    """
    Executed when the map starts. Check the host to see if there are any
    later versions. Debug the output of the results.
    
    TODO: Make sure that we somehow get more attention.
    
    @param event_var es.EventInfo
    """
    if int(checkForUpdates):
        reCacheConnection()
        cache = connection.getCache()
        if cache is not None:
            es.dbgmsg(0, cache)
            es.log(cache)
        
def checkUpdateCommand(args):
    """
    Executed when the 'checkupdates' command is used. Assume we want to force
    the update and print the cache.
    
    @param tuple|mixed args Any further arguments which were passed into the cmd
    """
    reCacheConnection(True)
    cache = connection.getCache()
    if cache is not None:
        es.dbgmsg(0, cache)
        
def reCacheConnection(forceRecache=False):
    """
    Reconnect to the server to check for updates. This overwrites the cache.
    Sends version variables to the server to warn of any version issues for
    security updates, etc.
    
    @param bool forceRecache Whether or not it will ignore if the connection
                             already has a cache.
    """
    if not connection.hasCache() or forceRecache is True:
        data = {}
        data["eventscripts_ver"] = str(es.getString("eventscripts_ver"))
        data["es_corelib_ver"] = str(es.getString("es_corelib_ver"))
        data["eventscripts_ver_revision"] = str(es.getString("eventscripts_ver_revision"))
        data["eventscripts_xa"] = str(es.getString("eventscripts_xa"))
        data["os.name"] = os.name
        data["game"] = es.getGameName()
        data["hostport"] = str(es.getString("hostport")) 
        try:
          l = es.getInt("hostip") 
          data["hostip"] = '%d.%d.%d.%d' % (l>>24 & 255, l>>16 & 255, l>>8 & 255, l & 255)
        except:
          # oh well, skip the IP address
          es.dbgmsg(1, "es_checkversion: Couldn't get IP address properly")
          pass
        connection.data = data
        connection.connect()
        connection.reCacheUpdate()
        connection.disconnect()