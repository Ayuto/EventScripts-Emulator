# ./addons/eventscripts/corelib/es_install/es_install.py

import cmdlib
import es
import esamlib
import installlib
import os.path
import io
import time

import psyco
psyco.full()


installlib._executeAutoLoad() # Automatically loads installed addons marked for autoload

###

class InstallLog(esamlib.DBGLog):
   """ Class to log es_install activity """
   logpath = es.getAddonPath('corelib/es_install') + '/es_install.log'

   def __init__(self, logpath=None):
      if not logpath is None:
         self.logpath = logpath

      self.lines  = []
      self.recent = []

      self._readLines()

   def _readLines(self):
      """ Populates the lines class variable with the existing log file """
      if not os.path.isfile(self.logpath): return

      logfile    = open(self.logpath)
      self.lines = logfile.readlines()
      logfile.close()

   def write(self, text, dbglvl=None):
      """ Writes logged text to the log file """
      if not dbglvl is None:
         es.dbgmsg(dbglvl, text)

      self.lines.append(time.strftime('%x %X ] ') + text + '\n')
      self.recent.append(time.strftime('%X ] ') + text + '\n')

      logfile = open(self.logpath, 'w')
      logfile.writelines(self.lines)
      logfile.close()

   def echo(self, recent=True):
      """ Display entire log or recent entries to server console """
      for line in self.recent if recent else self.lines:
         es.dbgmsg(0, line[:~0])

log = InstallLog()

###

def _registerServerCommand(name, description, callback):
   """
   Registers a server command prefixed by "es_" and "es_x"
   Commands prefixed with "es_" are sent to the expand_cmd function
   """
   cmdlib.registerServerCommand('es_' + name, expand_cmd, description, True)
   cmdlib.registerServerCommand('es_x' + name, callback, description, True)


def expand_cmd(args):
   """
   Commands sent here are prefixed with "es_". We change that prefix to "es_x",
   place the "es" server command in front of the command, and execute the result.
   """
   name = es.getargv(0)
   es.server.cmd('es ' + name[:3] + 'x' + name[3:] + ((' ' + str(args)) if len(args) else ''))


###


def install_cmd(args):
   """
   es_install [basename] [autoload]
   Uses installlib to install an addon by basename
   Alternatively, if no arguments are provided a list of installed addons is displayed
   """
   argc = len(args)
   # Installing an addon
   if argc in (1, 2):
      basename = args[0]
      autoload = (args[1] != '0') if argc == 2 else False

      installer = installlib.getInstaller(basename)
      if installer is None:
         log.write('es_install: Unable find addon on ESAM -- please ensure you have an active internet connection and the basename is valid', 0)

      else:
         status = installer.install(autoload)
         if status == installer.STATUS_SUCCESSFUL:
            log.write('es_install: %s installed successfully' % basename, 0)
         elif status == installer.STATUS_NO_DOWNLOAD:
            log.write('es_install: Unable to download %s -- please ensure you have an active internet connection' % basename, 0)
         elif status == installer.STATUS_ALREADY_DONE:
            log.write('es_install: %s already installed' % basename, 0)
         elif status == installer.STATUS_NOT_APPROVED:
            log.write('es_install: %s not approved for install' % basename, 0)
         else:
            log.write('es_install: Unknown error (%s)' % status, 0)

   # Getting a list of installed addons
   elif not argc:
      addonlist = installlib.infomanager.getInstalled()
      if addonlist:
         maxlength = max(list(map(len, addonlist)))

         es.dbgmsg(0, ' %s   Autoloaded\n %s   ----------' % ('Basename'.ljust(maxlength), '--------'.ljust(maxlength)))
         for addon in addonlist:
            es.dbgmsg(0, ' %s   %s' % (addon.ljust(maxlength), 'Yes' if installlib.getInstaller(addon, 1).isAutoLoaded() else 'No'))

      else:
         es.dbgmsg(0, 'No installed addons')

   # Invalid usage
   else:
      es.dbgmsg(0, 'Syntax: es_install <basename> [autoload]')
_registerServerCommand('install', 'Installs approved addons from the ESAM', install_cmd) # Registers es_install and es_xinstall as server commands


def update_cmd(args):
   """
   es_update <basename> [force update]
   Uses installlib to update an addon by basename
   """
   argc = len(args)
   if argc in (1, 2):
      basename = args[0]
      force    = (args[1] != '0') if argc == 2 else False

      installer = installlib.getInstaller(basename)
      if installer is None:
         log.write('es_install: Unable find addon on ESAM -- please ensure you have an active internet connection and the basename is valid', 0)

      else:
         status = installer.update(force)
         if status == installer.STATUS_SUCCESSFUL:
            log.write('es_update: %s updated successfully' % basename, 0)
         elif status == installer.STATUS_NO_DOWNLOAD:
            log.write('es_update: Unable to download %s -- please ensure you have an active internet connection' % basename, 0)
         elif status == installer.STATUS_NO_INSTALL_INFO:
            log.write('es_update: %s not installed with es_install' % basename, 0)
         elif status == installer.STATUS_ALREADY_DONE:
            log.write('es_update: %s already up to date' % basename, 0)
         elif status == installer.STATUS_NOT_APPROVED:
            log.write('es_update: %s not approved for install' % basename, 0)
         else:
            log.write('es_update: Unknown error (%s)' % status, 0)

   else:
      es.dbgmsg(0, 'Syntax: es_update <basename> [force update]')
_registerServerCommand('update', 'Updates addons installed with es_install', update_cmd) # Registers es_update and es_xupdate as server commands


def uninstall_cmd(args):
   """
   es_uninstall <basename>
   Uses installlib to uninstall an addon by basename
   """
   if len(args) == 1:
      basename  = args[0]
      installer = installlib.getInstaller(basename, io.StringIO())

      status = installer.uninstall()
      if status == installer.STATUS_SUCCESSFUL:
         log.write('es_uninstall: %s uninstalled successfully' % basename, 0)
      elif status == installer.STATUS_NO_INSTALL_INFO:
         log.write('es_uninstall: %s not installed' % basename, 0)
      else:
         log.write('es_uninstall: Unknown error (%s)' % status, 0)

   else:
      es.dbgmsg(0, 'Syntax: es_uninstall <basename>')
_registerServerCommand('uninstall', 'Uninstalls addons installed with es_install', uninstall_cmd) # Registers es_uninstall and es_xuninstall as server commands


"""
] es_uninstall teamfog
es_uninstall: teamfog not installed

] es_install teamfog 1
es_install: teamfog installed successfully
] es_install teamfog
es_install: teamfog already installed

] es_update teamfog
es_update: teamfog already up to date
] es_update teamfog 1
es_update: teamfog updated successfully

] es_uninstall teamfog
es_uninstall: teamfog uninstalled successfully

] es_update teamfog
es_update: teamfog not installed
"""