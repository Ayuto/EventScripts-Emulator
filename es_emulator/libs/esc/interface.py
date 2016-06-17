# -*- coding: utf-8 -*-

from . import addons
from .addon import Addon
from .parse import cleanpath
from .val import sv

def interface(func):
  def init(*args, **kwargs):
    result = func(*args, **kwargs)
    sv.save()
    return result
  return init

@interface
def loadaddon(addonname):
  try:
    return Addon(addonname).load(priority=True)
  except RuntimeError, IOError:
    return False
 
@interface
def unloadaddon(addonname):
  addonname = cleanpath(addonname)
  if addonname in addons:
    return addons[addonname].unload(priority=True)
  else:
    return False
   
@interface
def reloadaddon(addonname):
  addonname = cleanpath(addonname)
  if addonname in addons:
    return addons[addonname].reload(priority=True)
  else:
    return False
  
@interface
def enableaddon(addonname):
  addonname = cleanpath(addonname)
  if addonname in addons:
    return addons[addonname].enable(priority=True)
  else:
    return False
    
@interface
def disableaddon(addonname):
  addonname = cleanpath(addonname)
  if addonname in addons:
    return addons[addonname].disable(priority=True)
  else:
    return False
    
def addonexists(addonname):
  return cleanpath(addonname) in addons
    
def blockexists(addonname, block):
  addonname = cleanpath(addonname)
  return addonname in addons and block in addons[addonname].blocks
  
def eventexists(addonname, event):
  addonname = cleanpath(addonname)
  return addonname in addons and event in addons[addonname].events
  
def addonlist():
  return tuple((name, not addon.disabled) for name, addon in addons.iteritems())
