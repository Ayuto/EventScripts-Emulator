# -*- coding: utf-8 -*-

import os, es, esc
from es import getargv, getargc, getargs, getcmduserid
from . import addons, stack
from .parse import cleanpath, splitblocks
from .val import sv, ev

class Addon(object):
  
  addondir = sv('eventscripts_addondir')
  loadblock = 'load'
  unloadblock = 'unload'
  enableblock = 'enable'
  disableblock = 'disable'
  
  class Block(object):
    
    def __init__(self, name, code):
      self.name = name
      self.code = code
      
    def __call__(self):
      self.run(priority=True, userargs={'cmdname': getargv(0), 'argv': map(getargv, xrange(1, getargc())), 'args': getargs(), 'uid': int(getcmduserid())})
      sv.save()
      
    def run(self, priority=False, userargs=None):
      stack.queue(self.code, self.name, priority, userargs)
      
  class Event(Block):
    
    def __call__(self, event_var):
      self.run(priority=True)
      ev.varcache.clear()

  def __init__(self, scriptname):

    self.scriptname = cleanpath(scriptname)
    self.basename   = self.scriptname.split('/')[-1]
    self.scriptdir  = '%s/%s/' % (self.addondir, scriptname)
    self.scriptfile = '%ses_%s.txt' % (self.scriptdir, self.basename)
    self.pyscriptfile = '%s%s.py' % (self.scriptdir, self.basename)
      
    self.blocks = {}
    self.events = {}
    
  def scriptexists(self):
    return os.path.exists(self.scriptfile)
    
  def pyscriptexists(self):
    return os.path.exists(self.pyscriptfile)
    
  def load(self, priority=False):
    
    if self.scriptname in addons:
      raise RuntimeError, '[EventScripts] %s already loaded, try to es_unload it first' % self.scriptname
      
    if not self.scriptexists():
      raise IOError, 'Could not open script for %s' % self.scriptname

    script = open(self.scriptfile)
    code = splitblocks(script.readlines())
    script.close()
    
    for blockname, block in code['block'].iteritems():
      newblock = self.blocks[blockname] = self.Block('%s/%s' % (self.scriptname, blockname), block)
      es.addons.registerBlock(self.scriptname, blockname, newblock)

    for eventname, event in code['event'].iteritems():
      newevent = self.events[eventname] = self.Event('%s/%s' % (self.scriptname, eventname), event)
      es.addons.registerForEvent(self, eventname, newevent)

    self.disabled = False
    
    addons[self.scriptname] = self
    
    if self.loadblock in self.blocks:
      self.blocks[self.loadblock].run(priority)
      
    es.dbgmsg('corelib' in self.scriptname, 'Loaded %s' % self.scriptname)
    
    return True

  def unload(self, priority=False):
    
    es.dbgmsg(0, 'Unloading %s...' % self.scriptname)
    
    if self.unloadblock in self.blocks:
      self.blocks[self.unloadblock].run(priority)
      
    for block in self.blocks:
      es.addons.unregisterBlock(self.scriptname, block)
    for event in self.events:
      es.addons.unregisterForEvent(self, event)
      
    es.dbgmsg(0, '%s has been unloaded' % self.scriptname)
      
    self.blocks.clear()
    self.events.clear()
    del addons[self.scriptname]
    
    return True
    
  def reload(self, priority=False):
    self.unload(priority)
    self.load(priority)

  def enable(self, priority=False):
    es.dbgmsg(0, 'Enabling %s...' % self.scriptname)
    self.disabled = False
    if self.enableblock in self.blocks:
      self.blocks[self.enableblock].run(priority)
    return True
    
  def disable(self, priority=False):
    es.dbgmsg(0, 'Disabling %s...' % self.scriptname)
    self.disabled = True
    if self.disableblock in self.blocks:
      self.blocks[self.disableblock].run(priority)
    return True


import os
_proc_status = '/proc/%d/status' % os.getpid()

_scale = {'kB': 1024.0, 'mB': 1024.0*1024.0,
          'KB': 1024.0, 'MB': 1024.0*1024.0}

def _VmB(VmKey):
    '''Private.
    '''
    global _proc_status, _scale
     # get pseudo file  /proc/<pid>/status
    try:
        t = open(_proc_status)
        v = t.read()
        t.close()
    except:
        return 0.0  # non-Linux?
     # get VmKey line e.g. 'VmRSS:  9999  kB\n ...'
    i = v.index(VmKey)
    v = v[i:].split(None, 3)  # whitespace
    if len(v) < 3:
        return 0.0  # invalid format?
     # convert Vm value to bytes
    return float(v[1]) * _scale[v[2]]


def memory(since=0.0):
    '''Return memory usage in bytes.
    '''
    return _VmB('VmSize:') - since


def resident(since=0.0):
    '''Return resident memory usage in bytes.
    '''
    return _VmB('VmRSS:') - since


def stacksize(since=0.0):
    '''Return stack size in bytes.
    '''
    return _VmB('VmStk:') - since
