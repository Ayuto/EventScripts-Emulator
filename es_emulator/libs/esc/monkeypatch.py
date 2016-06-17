# -*- coding: utf-8 -*-

# TODO: Nuke, obviously.

usercmds = {}  # User command names and blocks
pyaddons  = lambda: ['/'.join(addon.__name__.split('.')[1:]) for addon in es.addons.AddonList]

from . import addons

import es, os, interface, parse

def pyscriptexists(addonname):
  return os.path.exists('%s/%s/%s.py' % (es.getString('eventscripts_addondir'), addonname, addonname.split('/')[-1]))
    
def monkeypatch(function, esfunc=None):
  if hasattr(es, function.__name__):
    esfunc = getattr(es, function.__name__)
  setattr(es, function.__name__, function)
  return esfunc
  
  
# The following serve (pretty much) as examples of how the es functions need to behave for compatibility with esc

@monkeypatch
def load(addonname):
  if pyscriptexists(addonname):
    load(addonname)
  else:
    interface.loadaddon(addonname)

@monkeypatch
def unload(addonname):
  if addonname in pyaddons():
    unload(addonname)
  else:
    interface.unloadaddon(addonname)
    
@monkeypatch
def reload(addonname):
  es.unload(addonname)
  es.load(addonname)
  
@monkeypatch
def enable(addonname):
  if addonname in pyaddons():
    enable(addonname)
  else:
    interface.enableaddon(addonname)

@monkeypatch
def disable(addonname):
  if addonname in pyaddons():
    disable(addonname)
  else:
    interface.disableaddon(addonname)

@monkeypatch
def exists(attribute, arg, *args):
  if attribute == 'script':
    return arg in pyaddons() or interface.addonexists(arg)
  if attribute == 'block':
    if arg in pyaddons():
      return arg in es.addons.Blocks
    else:
      block = parse.splitblock(arg)
      return block and interface.blockexists(*block)
  return exists(attribute, arg, *args)
  
@monkeypatch
def createscriptlist(match=None):
  pyads = pyaddons()
  if not match:
    return dict(
      [(script, {'type': 'py', 'status': 'enabled'}) for script in pyads] +
      [(script, {'type': 'txt', 'status': 'enabled' if enabled else 'disabled'}) for script, enabled in interface.addonlist()]
    )
  if es.exists('script', match):
    a = {match: {}}
    a[match]['type'] = 'py' if match in pyads else 'txt'
    a[match]['status'] = 'enabled' if match in pyads else ('disabled' if addons[match].disabled else 'enabled')
    return a
  return {}
