# ./addons/eventscripts/_libs/python/installlib.py

import pickle
import es
import os
import path
import zipfile

###

class InstallInfo(object):
   """
   Class for keeping installation information for an addon
   Information stored includes basename, version, files, and directories
   """
   version = ''

   def __init__(self, basename):
      self.basename = basename
      self.files    = set()
      self.dirs     = set()

   def getVersion(self):
      """ Returns the stored version of the addon """
      return self.version

   def setVersion(self, version):
      """ Sets the stored version of the addon """
      self.version = version

   def addFile(self, file):
      """ Marks a file as belonging to the addon """
      self.files.add(file)

   def getFiles(self):
      """ Returns a set of files belonging to the addon """
      return self.files.copy()

   def addDir(self, dir):
      """ Marks a directory as belonging to the addon """
      self.dirs.add(dir)

   def getDirs(self):
      """ Returns a set of directories belonging to the addon """
      return self.dirs.copy()


class InstallInfoManager(object):
   """ Class that manages InstallInfo instaces on disk """
   infopath = es.getAddonPath('_libs') + '/python/installinfo/'

   def __init__(self):
      """ Creates the installinfo directory if it doesn't exist """
      if not os.path.isdir(self.infopath):
         os.mkdir(self.infopath)

   def getInfoPath(self, basename):
      """ Returns the absolute path to a basename's install info """
      return self.infopath + basename + '.db'

   def hasInstallInfo(self, basename):
      """ Returns True if the basename has registered InstallInfo otherwise returns False """
      return os.path.isfile(self.getInfoPath(basename))

   def getInstallInfo(self, basename):
      """ Returns the InstallInfo instance for the basename """
      if self.hasInstallInfo(basename):
         infofile = open(self.getInfoPath(basename))
         info     = pickle.load(infofile)
         infofile.close()
      else:
         info = InstallInfo(basename)

      return info

   def saveInstallInfo(self, basename, info):
      """ Saves the InstallInfo instance provided to the basename """
      infofile = open(self.getInfoPath(basename), 'w')
      pickle.dump(info, infofile)
      infofile.close()

   def getInstalled(self):
      """ Returns a list of basenames that have InstallInfo instances """
      return [addon[addon.replace('\\', '/').rfind('/') + 1:~2] for addon in [x for x in os.listdir(self.infopath) if x.endswith('.db')]]

infomanager = InstallInfoManager()

###

class Addon(object):
   """ Base Addon object that holds required attributes and functions for use with AddonInstaller """
   infomanager = infomanager
   addon_file  = None

   def __init__(self, basename, addon_file):
      """
      Along with basename the Addon object also requires the addon file
      That addon file when be given when the download function is called
      """
      self.basename   = basename
      self.addon_file = addon_file

      self.approved       = '1'
      self.currentversion = ''
      self.es_load        = basename

   def download(self):
      """ Returns the addon file given in the initialization function """
      return self.addon_file

###

class AddonInstaller(object):
   """ Class that handles the installing, updating, and uninstalling of addons """
   # Status attributes returned by install, update, and uninstall
   STATUS_SUCCESSFUL      = 0
   STATUS_NO_DOWNLOAD     = 1
   STATUS_NO_INSTALL_INFO = 2
   STATUS_ALREADY_DONE    = 4
   STATUS_NOT_APPROVED    = 8

   # Useful attributes
   gamepath     = str(es.ServerVar('eventscripts_gamedir')) + '/'
   autoloadpath = es.getAddonPath('_autoload') + '/'

   def __init__(self, addon):
      """ Installation of an addon requires an Addon-based class instance """
      self.addon    = addon
      self.addondir = es.getAddonPath(self.addon.es_load) + '/'

   """ Query functions """

   def isInstalled(self):
      """ Returns True if the addon is installed otherwise returns False """
      filename = self.addon.es_load.split('/')[~0]
      return bool(list(filter(os.path.isfile, (self.addondir + filename + '.py', self.addondir + 'es_' + filename + '.txt')))) or self.addon.infomanager.hasInstallInfo(self.addon.basename)

   def isAutoLoaded(self):
      """ Returns True if the addon is autoloaded otherwise returns False """
      return os.path.isfile(self.autoloadpath + self.addon.basename + '.cfg')

   def setAutoload(self, state):
      """ Sets or removes autoload for the addon based on "state" """
      autoloadpath = self.autoloadpath + self.addon.basename + '.cfg'

      if state:
         autoloadfile = open(autoloadpath, 'w')
         autoloadfile.write('es_xload ' + self.addon.es_load + '\n')
         autoloadfile.close()

      elif os.path.isfile(autoloadpath):
         os.remove(autoloadpath)

   """ File manipulation functions """

   def install(self, autoload=False, addon_file=None):
      """
      Installs the addon, setting autoload if necessary. If the optional
      "addon_file" keyword is provided that file will be used in lieu of
      downloading the addon from the ESAM.
      """
      if self.isInstalled(): return self.STATUS_ALREADY_DONE

      if self.addon.approved != '1': return self.STATUS_NOT_APPROVED

      addon_file = self.addon.download() if addon_file is None else addon_file
      if not addon_file: return self.STATUS_NO_DOWNLOAD

      self._extract(addon_file, InstallInfo(self.addon.basename))
      self.setAutoload(autoload)

      return self.STATUS_SUCCESSFUL

   def update(self, force=False):
      """
      Updates the addon it "force" is True or the ESAM version number is different
      from the installed version number.
      """
      if not self.addon.infomanager.hasInstallInfo(self.addon.basename): return self.STATUS_NO_INSTALL_INFO

      if self.addon.approved != '1': return self.STATUS_NOT_APPROVED

      installinfo = self.addon.infomanager.getInstallInfo(self.addon.basename)
      if not force and installinfo.getVersion() == self.addon.currentversion and installinfo.getVersion(): return self.STATUS_ALREADY_DONE

      autoload   = self.isAutoLoaded()
      addon_file = self.addon.download()
      if not addon_file: return self.STATUS_NO_DOWNLOAD

      status = self.uninstall(installinfo)
      if status != self.STATUS_SUCCESSFUL: return status

      return self.install(autoload, addon_file)

   def uninstall(self, installinfo=None):
      """
      Unloads the addon if it is loaded
      Uninstalls the addon using the InstallInfo of the addon
      """
      if installinfo is None:
         if not self.addon.infomanager.hasInstallInfo(self.addon.basename): return self.STATUS_NO_INSTALL_INFO
         installinfo = self.addon.infomanager.getInstallInfo(self.addon.basename)

      if self.addon.es_load in self._getAddonSet(): es.unload(self.addon.es_load)

      for filename in filter(os.path.isfile, installinfo.getFiles()):
         os.remove(filename)

      for dir in filter(os.path.isdir, sorted(installinfo.getDirs(), reverse=True)):
         if not os.listdir(dir):
            os.rmdir(dir)

      for path in filter(os.path.isfile, (self.autoloadpath + self.addon.basename + '.cfg', self.addon.infomanager.getInfoPath(self.addon.basename))):
         os.remove(path)

      return self.STATUS_SUCCESSFUL

   """ Internal functions """

   def _extract(self, addon_file, installinfo):
      """ Extracts the zip file "addon_file" while updating InstallInfo instance "installinfo" """
      addon_zip = zipfile.ZipFile(addon_file)
      ziplist   = sorted(addon_zip.namelist())

      # Adds each directory to the addon's install info and creates the directory if necessary
      for dir in [x for x in ziplist if x.endswith('/')]:
         installinfo.addDir(self.gamepath + dir)

         if not os.path.isdir(self.gamepath + dir):
            os.mkdir(self.gamepath + dir)

      # Adds the __init__.py and __init__.pyc files that will be generated to the list of files associated with the addon
      init_path = es.getAddonPath(self.addon.es_load) + '/__init__.py'
      installinfo.addFile(init_path)
      installinfo.addFile(init_path + 'c')

      # Adds each file's path to the addon's install info and extracts the file
      for filename in [x for x in ziplist if not x.endswith('/')]:
         installinfo.addFile(self.gamepath + filename)
         if filename.endswith('.py'): # Assume every .py file will generate a .pyc
            installinfo.addFile(self.gamepath + filename + 'c')

         newfile = path.path(self.gamepath + filename)
         newfile.write_bytes(addon_zip.read(filename))

      # Stores the version number for update purposes and saves the install info for the addon
      installinfo.setVersion(self.addon.currentversion)
      self.addon.infomanager.saveInstallInfo(self.addon.basename, installinfo)

      addon_zip.close()

   def _getAddonSet(self):
      """ Returns a set of all ESS and ESP addons """
      addon_list = set(es.createscriptlist())

      for addon in es.addons.getAddonList():
         addon_list.add(addon.__name__[:addon.__name__.rfind('.')].replace('.', '/'))

      return addon_list


import esamlib # Don't move this! Some stuff in esamlib depends on the above installlib classes.

def getInstaller(basename, addon_file=None, log=esamlib.dbglog):
   """
   Returns an AddonInstaller instance for the given basename. When "addon_file"
   is provided it will be the zip file installed, otherwise esamlib will provide
   the zip file from the ESAM.
   """
   addon = Addon(basename, addon_file) if addon_file else esamlib.getAddon(basename, log)
   return None if addon is None else AddonInstaller(addon)

def getInstallerFromPath(basename, path, log=esamlib.dbglog):
   """ Returns an AddonInstaller instance for a zip on disk """
   return getInstaller(basename, open(path ,'rb'), log)

###

def _executeAutoLoad():
   """ Loads all installed addons marked for automatic loading """
   autoloadpath = es.getAddonPath('_autoload') + '/'

   if not os.path.isdir(autoloadpath):
      os.mkdir(autoloadpath)

   for filename in [x for x in os.listdir(autoloadpath) if x.endswith('.cfg') and os.path.isfile(autoloadpath + x)]:
      es.server.queuecmd('es_xmexec ../addons/eventscripts/_autoload/' + filename)

"""
>>> import installlib

>>> randmaps = installlib.getInstaller('randmaps')
>>> randmaps.install(True) # Install RandMaps with it autoloaded
0 # Install successful

>>> randmaps.update()
4 # Already up to date
>>> randmaps.update(True) # Force update
0 # Update successful

>>> randmaps.uninstall()
0 # Uninstall successful
"""
"""
import es
import installlib

basename = 'iptocountry' # Change to the name of your addon

# Designate a file as part of your addon, to be cleaned up when updated or uninstalled
installinfo = installlib.infomanager.getInstallInfo(basename)
installinfo.addFile(es.getAddonPath('_libs') + '/python/iptocountry.db') # This file is generated by IPToCountry
installlib.infomanager.saveInstallInfo(basename, installinfo)
"""
