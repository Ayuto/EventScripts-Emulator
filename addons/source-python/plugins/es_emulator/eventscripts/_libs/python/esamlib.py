# ./addons/eventscripts/_libs/python/esamlib.py

import base64
import es
import os.path
import io
import sys
import urllib.request, urllib.error, urllib.parse
import xml.etree.ElementTree as ElementTree

"""
Basic Library for interfacing with the ESAM
"""

baseurl = 'http://addons.eventscripts.com/' # Base URL to ESAM

###

class DBGLog(object):
   """ Base Class for logging installlib information """
   def __init__(self):
      self.lines = []

   def write(self, text, dbglvl=None):
      """ Writes the text to log, echoing to the console if necessary """
      if not dbglvl is None:
         es.dbgmsg(dbglvl, text)

      self.lines.append(text)

   def echo(self):
      """ Outputs stored log lines to the console """
      for line in self.lines:
         es.dbgmsg(0, line)

dbglog = DBGLog()

###

class ESAMUpload(object):
   """ Class for submitting information to the ESAM """
   """
   Keyword arguments:
   # username - full username.
   # password - password in plain text.
   # basename - basename
   # filename - name of file.
   # filesize - size of file in bytes
   # file_extension - file extension (zip, py, or txt only)
   # version_notes - version notes.
   # version - file version
   # b64_file_content - binary file contents in base64 encoded.
   # addon_name - addon name
   # forum_url - full URL to forum thread (The THREAD not POST (requires ?t=XXXX url)
   # public_variable - public variable for script
   # addon_desc - addon description
   # es_version - minimal ES version required.
   # video_url - full URL to youtube video.
   # addon_summary - 255 character summary for addon.
   # ready4approval - 1/0 flag if addon is ready for approval
   # install_instructions - installation instructions
   # featurelist_url - full featurelist URL (leave blank if none)
   # es_load_args - es_load arguments (ie es_load mugmod or es_load /wcs/myrace/clown
   # status - status of addon in plain text (Hidden or Normal)
   """
   # Reference URLs
   uploadurl = baseurl + 'sdk/upload'
   addurl    = baseurl + 'sdk/add_collaborator'
   removeurl = baseurl + 'sdk/remove_collaborator '

   """ Public functions """

   def addCollaborator(self, username, api_key, basename, collaborator):
      """ Adds a collaborator to an addon on the ESAM """
      return self.kw_post(self.addurl, username=username, api_key=api_key, basename=basename, collaborator=collaborator)

   def removeCollaborator(self, username, api_key, basename, collaborator):
      """ Removes a collaborator from an addon on the ESAM """
      return self.kw_post(self.removeurl, username=username, api_key=api_key, basename=basename, collaborator=collaborator)

   def upload(self, username, api_key, basename, path, addon_name, version, version_notes, addon_desc,
    addon_summary, es_load_args, es_version, forum_url='', public_variable='', video_url='', install_instructions='',
    featurelist_url='', ready4approval=False, status='Normal'):
      """ Uploads a file to the ESAM """

      filesize = os.path.getsize(path)
      filename = path.replace('\\', '/').rsplit('/', 1)[1]
      file_extension = filename.rsplit('.', 1)[1]

      f = open(path, 'rb')
      b64_file_content = base64.encodestring(f.read())
      f.close()

      return self.kw_post(self.uploadurl, username=username, api_key=api_key, basename=basename, filename=filename, filesize=filesize,
       file_extension=file_extension, version_notes=version_notes, version=version, b64_file_content=b64_file_content,
       addon_name=addon_name, forum_url=forum_url, public_variable=public_variable, addon_desc=addon_desc,
       es_version=es_version, video_url=video_url, addon_summary=addon_summary, ready4approval=int(ready4approval),
       install_instructions=install_instructions, featurelist_url=featurelist_url, es_load_args=es_load_args, status=status)

   """ Private functions """

   def kw_post(self, *a, **kw):
      """ Internal function: Sends encoded data to an url """
      if len(a) != 1: raise TypeError(f'kw_post takes exactly 1 argument ({len(a)} given)')
      u = urllib.request.urlopen(a[0], data=urllib.parse.urlencode(kw))
      d = u.read()
      u.close()

      return d

esamupload = ESAMUpload()

def addCollaborator(*a, **kw):
   return esamupload.addCollaborator(*a, **kw)
addCollaborator.__doc__ = ESAMUpload.addCollaborator.__doc__

def removeCollaborator(*a, **kw):
   return esamupload.removeCollaborator(*a, **kw)
removeCollaborator.__doc__ = ESAMUpload.removeCollaborator.__doc__

def upload(*a, **kw):
   return esamupload.upload(*a, **kw)
upload.__doc__ = ESAMUpload.upload.__doc__

"""
# API keys can be obtained from: http://addons.eventscripts.com/manage/api_key/

# Upload to in-use basename gungame3
>>> esamlib.upload('SuperDave', my_api_key, 'gungame3', 'c:\\Redirect.zip', 'Redirect', '1.0', 'Version notes', 'Another SD test upload', 'Test summary', 'redirect', '2.0')
'Error: Basename in use by another user.'

# Upload to available basename sd_redirect
>>> esamlib.upload('SuperDave', my_api_key, 'sd_redirect', 'c:\\Redirect.zip', 'Redirect', '1.0', 'Version notes', 'Another SD test upload', 'Test summary', 'redirect', '2.0')
'Success! Addon ID# 16569'

# Add GODJonez as a collaborator on the redirect project
>>> esamlib.addCollaborator('SuperDave', my_api_key, 'sd_redirect', 'GODJonez')
'GODJonez added successfully to sd_redirect'

# Remove GODJonez as a collaborator on the redirect project
>>> esamlib.removeCollaborator('SuperDave', my_api_key, 'sd_redirect', 'GODJonez')
'GODJonez removed successfully from sd_redirect'
"""

###

# Search type constants
SEARCH_ADDON       = 'addon' # addon - Searchs multiple fields within an addon. (name, desc, etc)
SEARCH_DESCRIPTION = 'desc'  # desc  - Addon description
SEARCH_ESVERSION   = 'esmin' # esmin - All addons by minimum ES version
SEARCH_NAME        = 'name'  # name  - Addon Name
SEARCH_PUBLICVAR   = 'pvar'  # pvar  - All addons by a public variable
SEARCH_USER        = 'user'  # user  - All addons by a user

# Top query constants
TOP_ADDONCOUNT = 'addons' # Unavailable for topAddons
TOP_DOWNLOADS  = 'downloads'
TOP_WOOTS      = 'woots'

class ESAMQuery(object):
   """ Class for querying ESAM addon database """
   # URLs used for addon searching
   searchurl    = baseurl + 'sdk/search/'
   updateurl    = baseurl + 'sdk/updatedsince/'
   topuserurl   = baseurl + 'sdk/topuser'
   topaddonsurl = baseurl + 'sdk/topaddon'
   watchedurl   = baseurl + 'sdk/watched_addons/'
   getcollaburl = baseurl + 'sdk/collaborators/'
   getbasename  = baseurl + 'sdk/getbasename/'
   checkdep     = baseurl + 'sdk/checkDependencies/'

   """ Public functions """

   def getCollaborators(self, basename):
      """
      Returns a tuple in the format: (leader, collaborators)
      Where collaborators is a list.
      """
      u = urllib.request.urlopen(self.getcollaburl + basename)
      data = ElementTree.XML(u.read())
      u.close()
      return data.findtext('leader'), [x.text for x in data.getiterator('collaborator')]

   def search(self, searchtype, text):
      """ Returns a list of addons matching the search text of the search type """
      return self.getXMLList(self.searchurl + text + '/' + searchtype, 'addon')

   def topAddons(self, sortby, count=10):
      """ Returns a list of top addons sorted by the given sort constant """
      if sortby == TOP_ADDONCOUNT: raise ValueError('TOP_ADDONCOUNT is not a valid sort for topAddons')
      return self.getXMLList(self.topaddonsurl + sortby + '/%i' % count, 'addon')

   def topUsers(self, sortby, count=10):
      """ Returns a list of top users sorted by the given sort constant """
      return self.getXMLList(self.topuserurl + sortby + '/%i' % count, 'user')

   def updated_since(self, timestamp):
      """ Returns a list of addons updated since the given Unix time """
      return self.getXMLList(self.updateurl + int(timestamp), 'addon')

   def watchedBy(self, username):
      """ Returns a list of addons watched by the given username """
      u = urllib.request.urlopen(self.watchedurl + base64.b64encode(username))
      data = ElementTree.XML(u.read())
      u.close()
      return self.spliceBy(data.find('watched'), 'addon')

   def getBaseName(self, addonid):
      """ Returns an addon's basename by addon id """
      u = urllib.request.urlopen(self.getbasename + str(addonid))
      data = u.read()
      u.close()
      return data

   def checkDependencies(self, basename):
      """ Returns the dependicies of an addon by basename """
      return self.getXMLList(self.checkdep + basename, 'dependency')

   """ Data-manipulation functions """

   def getXMLList(self, url, searchname):
      """ Returns a list information from the XML returned by an URL """
      u = urllib.request.urlopen(url)
      data = ElementTree.XML(u.read())
      u.close()
      return self.spliceBy(data, searchname)

   def spliceBy(self, data, searchname):
      """ Returns a list of information in the given XML data that matches the given searchname """
      result = []
      for item in data.findall(searchname):
         item_data = {}
         for subitem in item.getiterator():
            name  = subitem.tag
            value = item.findtext(name)
            if value:
               item_data[name] = value

         if item_data:
            result.append(item_data)

      return result

esamquery = ESAMQuery()

def getCollaborators(*a, **kw):
   return esamquery.getCollaborators(*a, **kw)
getCollaborators.__doc__ = ESAMQuery.getCollaborators.__doc__

def search(*a, **kw):
   return esamquery.search(*a, **kw)
search.__doc__ = ESAMQuery.search.__doc__

def topAddons(*a, **kw):
   return esamquery.topAddons(*a, **kw)
topAddons.__doc__ = ESAMQuery.topAddons.__doc__

def topUsers(*a, **kw):
   return esamquery.topUsers(*a, **kw)
topUsers.__doc__ = ESAMQuery.topUsers.__doc__

def updated_since(*a, **kw):
   return esamquery.updated_since(*a, **kw)
updated_since.__doc__ = ESAMQuery.updated_since.__doc__

def watchedBy(*a, **kw):
   return esamquery.watchedBy(*a, **kw)
watchedBy.__doc__ = ESAMQuery.watchedBy.__doc__

def getBaseName(*a, **kw):
   return esamquery.getBaseName(*a, **kw)
getBaseName.__doc__ = ESAMQuery.getBaseName.__doc__

def checkDependencies(*a, **kw):
   return esamquery.checkDependencies(*a, **kw)
checkDependencies.__doc__ = ESAMQuery.checkDependencies.__doc__

"""
# Unless otherwise specified, query functions return a list (in order, if meaningful) of dictionaries of addon/user information.

# Query the leader and collaborators of an addon with the return format (leader, [collaborators,])
>>> esamlib.getCollaborators('sentrysounds')
('Mattie', ['HellenAngel'])

# Query [NATO]Hunter's addons
>>> result = esamlib.search(esamlib.SEARCH_USER, 'Hunter')

# Query all addons that require at least ES 2.1
>>> result = esamlib.search(esamlib.SEARCH_ESVERSION, '2.1')

# Query the top four addons by woots
>>> result = esamlib.topAddons(esamlib.TOP_WOOTS, 4)

# Query the top three users by number of addons
>>> result = esamlib.topUsers(esamlib.TOP_ADDONCOUNT, 3)

# Query the top ten users by downloads
>>> result = esamlib.topUsers(esamlib.TOP_DOWNLOADS)

# Query the addons updated less than one day ago
>>> result = esamlib.updated_since(time.time() - 86400)

# Query addons watched by XE_ManUp
>>> result = esamlib.watchedBy('XE_ManUp')
"""

###

import installlib # Don't move this

class ESAMAddon(installlib.Addon):
   """ Class that wraps the ESAM SDK and also provides basic addon download """
   baseurl = baseurl

   def __init__(self, xmldata, log=dbglog):
      self.data = xmldata
      self.log  = log

   def __getattr__(self, name):
      """
      Available attributes include:
         - id
         - author
         - authorid
         - name
         - basename
         - approved
         - es_load
         - date
         - woots
         - desc
         - summary
         - currentversion
         - versionnotes
         - video
         - defaultssid
         - downloadcount
      """
      return_val = self.get(name)

      if return_val is None:
         raise AttributeError(f"Addon {self.basename} has no '{name}' attribute")

      return return_val

   def download(self):
      """ Returns a file instance of the addon's latest downloadable version """
      if self.approved != '1': return None

      try:
         u    = urllib.request.urlopen(self.baseurl + 'addons/download/' + self.basename)
         es.dbgmsg(0, self.baseurl + 'addons/download/' + self.basename)
         addon = io.StringIO(u.read())
         u.close()

         return addon

      except IOError:
         info = sys.exc_info()
         self.log.write(f'ESAMLib: {info[0].__name__} - {info[1]}', 2)

      return None

   def get(self, attribute):
      """ Returns an attribute of the addon by name """
      return self.data.findtext(attribute) if self.data else None

   def getElements(self):
      """ Returns a list of the addon's elements """
      return self.data.getiterator() if self.data else []

   def getElementNames(self):
      """ Returns a list of the names of the addon's elements """
      return [x.tag for x in self.getElements()]


def getAddon(basename, log=dbglog):
   """ Returns an ESAMAddon instance for the basename """
   try:
      u    = urllib.request.urlopen(baseurl + 'sdk/addoninfo/' + basename)
      data = u.read()
      u.close()

      if not data: return None
      xml = ElementTree.XML(data).find('addon')
      return ESAMAddon(xml, log) if xml else None

   except IOError:
      info = sys.exc_info()
      log.write(f'ESAMLib: {info[0].__name__} - {info[1]}', 2)

   return None

###

class ESAMUser(object):
   """ Class that holds ESAM user information for query """
   class UserAddons(object):
      """ Class that allows access to an user's addons through an ESAMUser instance """
      def __init__(self, data, log=dbglog):
         self.data = data
         self.log  = log

         self.addons = {}

      def __getattr__(self, name):
         """ Allows attribute access to the user's addons """
         return_val = self.find(name)

         if return_val is None:
            raise AttributeError(f'UserAddons instance has no \'{name}\' attribute')

         return return_val

      def find(self, addonname):
         """ Finds and returns an addon as an ESAMAddon instance by its basename """
         if addonname in self.addons: return self.addons[addonname]

         for addon in self.getAddonList():
            if addonname == addon.findtext('basename'):
               return_addon = self.addons[addonname] = ESAMAddon(addon, self.log)
               return return_addon

         return None

      def isAddon(self, basename):
         """ Returns True if the basename is in the addon list of the user otherwise returns False """
         return basename in self.getAddonNameList()

      def getAddonList(self):
         """ Returns the addon elements for all the user's addons """
         return self.data.findall('addon')

      def getAddonNameList(self):
         """ Returns a list of addon basenames for the user """
         return [x.findtext('basename') for x in self.getAddonList()]

   """
   Begin User class
   A farily light "wrapper" around the ESAM SDK for user data
   """

   def __init__(self, xmldata, addondata, log=dbglog):
      self.xmldata = xmldata
      self.addons  = self.UserAddons(addondata, log)

   def __getattr__(self, name):
      """
      Available attributes include:
         - username
         - userid
         - addontotal
         - addonrank
         - woottotal
         - wootrank
         - downloadtotal
         - downloadrank
      """
      return_val = self.get(name)

      if return_val is None:
         raise AttributeError(f"ESAMUser instance with has no '{name}' attribute")

      return return_val

   def get(self, attribute):
      """ Returns user information by element name """
      return self.xmldata.findtext(attribute) if self.xmldata else None

   def getElements(self):
      """ Returns a list of elements of user information """
      return self.xmldata.getiterator() if self.xmldata else []

   def getElementNames(self):
      """ Returns a list of element names that can be queried about the user """
      return list(filter(self.get, [x.tag for x in self.getElements()]))


def getUser(username, log=dbglog):
   """ Returns an ESAMUser instance for the username """
   try:
      u   = urllib.request.urlopen(baseurl + 'sdk/getuserid/' + base64.b64encode(username))
      tid = u.read()
      u.close()

      if tid == "false" or not tid: return None

      u       = urllib.request.urlopen(baseurl + 'sdk/getuserinfo/' + tid)
      xmldata = ElementTree.XML(u.read())
      u.close()

      u         = urllib.request.urlopen(baseurl + 'sdk/getuseraddons/' + tid)
      addondata = ElementTree.XML(u.read())
      u.close()

      return ESAMUser(xmldata, addondata, log)

   except IOError:
      info = sys.exc_info()
      log.write(f'ESAMLib: {info[0].__name__} - {info[1]}', 2)

   return None

"""
>>> import esamlib

>>> sd = esamlib.getUser('SuperDave')

>>> sd.getElementNames()
['username', 'userid', 'addontotal', 'addonrank', 'woottotal', 'wootrank', 'downloadtotal', 'downloadrank']

>>> sd.username
'SuperDave'
>>> sd.userid
'11091'
>>> sd.downloadrank
'4'

>> sd.get('userid')
'11091'

>>> sd.addons.getAddonNameList()
['cheapbombtimer', 'regenmod', 'cheapzombie', 'cheapdeathmatch', 'gunmod', 'cheapwirecut', 'swapwithvictim', 'slomomod', 'slobot', 'knifegrenade', 'newrewards', 'cssoundtrack', 'cheapbleed', 'explosivedeaths', 'nadeslay', 'healmates', 'teamfog', 'healthregen', 'weaponstats', 'splashdamage', 'doublevip', 'cheapbeacon','nowyouseeme', 'coloredhealth', 'bomberman', 'sourceradar', 'ezrestrict', 'assistedkills', 'randmaps', 'iedmod', 'safespawn', 'ezfilter', 'extendedevents', 'iptocountry', 'cheapbulletwhizz', 'cheapemote']

>>> sd.addons.cssoundtrack
<esamlib.Addon object at 0x1173AB70>
>>> sd.addons.find('cssoundtrack')
<esamlib.Addon object at 0x1173AB70>

>>> sd.addons.cssoundtrack.getElementNames()
['addon', 'id', 'author', 'authorid', 'name', 'basename', 'approved', 'es_load', 'date', 'woots', 'desc', 'summary', 'currentversion', 'versionnotes', 'video', 'defaultssid']

>>> sd.addons.cssoundtrack.id
'13758'
>>> sd.addons.cssoundtrack.currentversion
'7'
>>> sd.addons.cssoundtrack.video
'http://www.youtube.com/v/G3S8l3BB4J0'
>>> sd.addons.cssoundtrack.woots
'21'
>>> sd.addons.cssoundtrack.date
'2007-05-02 04:21:26'
>>> sd.addons.cssoundtrack.defaultssid
'200'
"""
"""
>>> import esamlib

>>> css = esamlib.getAddon('cssoundtrack')

>>> css.getElementNames()
['addon', 'id', 'author', 'authorid', 'name', 'basename', 'approved', 'es_load', 'date', 'woots', 'desc', 'summary', 'currentversion', 'versionnotes', 'video', 'defaultssid']

>>> css.download()
<StringIO.StringIO instance at 0x115BF738>

>>> css.currentversion
'7'
>>> css.approved
'1'

>>> css.get('approved')
'1'
"""
