import es
from .. import addons
from ..addon import Addon
from ..parse import cleanpath, splitblock
from ..interface import blockexists
from . import Command
from ..val import sv

def pyaddons(addonlist=es.addons.AddonList):
  for addon in es.addons.AddonList:
    yield addon.__name__.partition('.')[-1].replace('.', '/')

@Command(syntax='[scriptname]', types=str, desc='Loads a script or lists all loaded scripts if no script is provided.')
def load(argv):
  if argv:
    addonname = cleanpath(argv[0])
    newaddon = Addon(addonname)
    if newaddon.pyscriptexists():
      sv.save()
      es.load(addonname)
    else:
      newaddon.load()
  else:
    es.dbgmsg(0, '[Eventscripts] Loaded:\n')
    for addonname in sorted(addons):
      es.dbgmsg(0, '[Eventscripts] [%sabled] %s' % ('dis' if addons[addonname].disabled else 'en', addonname))
    for addonname in sorted('/'.join(addon.__name__.split('.')[1:]) for addon in es.addons.AddonList):
      es.dbgmsg(0, '[Eventscripts] [enabled] %s' % addonname)

@Command(syntax='<scriptname>', types=str, desc='Unloads a script that has been loaded.')
def unload(argv):
  if argv:
    addonname = cleanpath(argv[0])
    if addonname in addons:
      addons[addonname].unload()
    elif addonname in pyaddons():
      sv.save()
      es.unload(addonname)
    else:
      raise RuntimeError, '%s was not loaded' % addonname
    
@Command(syntax='<scriptname>', types=str, desc='Reloads a script that is loaded.')
def _reload(argv):
  if argv:
    addonname = cleanpath(argv[0])
    if addonname in addons:
      addons[addonname].reload()
    elif addonname in pyaddons():
      sv.save()
      es.reload(addonname)
    else:
      load.run(argv)

@Command(syntax='<scriptname>', types=str, desc='Enables a script that has been loaded.')
def enable(argv):
  if argv:
    addonname = cleanpath(argv[0])
    if addonname in addons:
      addons[addonname].enable()
    elif addonname in pyaddons():
      sv.save()
      es.enable(addonname)
    else:
      raise RuntimeError, '%s was not loaded' % addonname
  
@Command(syntax='<scriptname>', types=str, desc='Disables a script that has been loaded.')
def disable(argv):
  if argv:
    addonname = cleanpath(argv[0])
    if addonname in addons:
      addons[addonname].disable()
    elif addonname in pyaddons():
      sv.save()
      es.disable(addonname)
    else:
      raise RuntimeError, '%s was not loaded' % addonname
  
@Command(syntax='<block>', types=str, desc='Executes a block.')
def doblock(argv):
  block = argv[0]
  split = splitblock(block)
  if split:
    addonname, blockname = split
    if blockexists(addonname, blockname):
      addons[addonname].blocks[blockname].run()
    else:
      sv.save()
      es.doblock(block)
