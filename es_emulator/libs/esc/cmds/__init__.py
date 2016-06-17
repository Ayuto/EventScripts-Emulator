# -*- coding: utf-8 -*-

import re, inspect, es, esc
from es import regcmd, getargv, getargc, getargs, dbgmsg, ForceServerCommand
from .. import commands, aliases, stack
from ..parse import getcode, expand, escompile, tokenize, join, argsfrom
from ..val import sv, VAR, Val


class Alias(object):
  
  BLOCK_PREFIX = 'esc.aliases'
  
  def __init__(self, name):
    self.name = 'alias: %s' % name
    es.addons.registerBlock(self.BLOCK_PREFIX, name, self)
    aliases[name] = self
    regcmd(name, '%s/%s' % (self.BLOCK_PREFIX, name))
    
  def getcode(self, args, n):
    self.code = getcode(args, n)
    
  def __call__(self):
    stack.queue(self.code, self.name, True) # TODO: insertlines rather than queue - deal with concommand... ES WILL FIX THIS
    
  def run(self):
    stack.insertlines(self.code)
    

class Command(object):
  
  BLOCK_PREFIX = 'esc.cmds'
  AUTOCREATE = sv.eventscripts_autocreate # TODO: Cache?
  
  _syntax_regex = re.compile(
    '<(?P<mand>[^>]+)>|' \
    '\[\[(?P<args>[^\]]+)\]\]|' \
    '\[(?P<opt>[^\]]+)\]|' \
    '(?P<lit>[^< \[\]]+)' \
  )
  
  _mandargs_regex = re.compile('<([^>]+)>|[()]')
  
  def __init__(self,
      desc=None,             # Command description
      pre=True,              # Use es and es_x prefix
      con=False,             # Send commandstring straight to console. TODO: remove after all commands are ported
      argsfrom=None,         # Stop tokenizing after index
      alt=None,              # Alternative name for command
      expand=True,           # Always expand when default command name
      syntax=None,           # Command syntax
      types=tuple(),         # Argument types
      reg=True,              # Register command
      remquotes=False,
    ):
      
    if syntax:
      syntaxlol = [filter(lambda t: t[1], match.groupdict().items())[0] for match in self._syntax_regex.finditer(syntax)]
      
    self.desc, self.pre, self.con, self.argsfrom, self.alt, self.expand, self.syntax, self.types, self.reg, self.remquotes = \
      desc, pre, con, argsfrom, alt, expand, syntax, types, reg, remquotes
      
    if self.types and not isinstance(self.types, tuple): self.types = (self.types,)
    self.minargs = 0 if self.syntax is None else len(self._mandargs_regex.findall(self.syntax))
    self.vars = [n for n, i in enumerate(self.types) if i is VAR] if self.types else []
    
  def __call__(self, method):
    
    if self.con: # TODO: remove when commands ported
      return self
    
    self.method = method
    self.name = method.__name__
    if self.name[0] == '_': # Necessary for reserved words in python e.g. can't have a function called 'if'
      self.name = self.name[1:]

    params = inspect.getargspec(self.method)[0]
    
    self.argv = 'argv' in params
    self.args = 'args' in params
    
    if self.pre:
      for prefix in ('es_', 'es_x'):
        commands['%s%s' % (prefix, self.name)] = self
    else:
      commands[self.name] = self
      if self.alt:
        commands[self.alt] = self
      
    self.expname = 'es_%s' % self.name if self.pre else self.name
    
    es.addons.registerBlock('esc.cmds', self.name, self.concommand)
    names = []
    if self.pre:
      names.append('es_%s' % self.name)
      names.append('es_x%s' % self.name)
    else:
      names.append(self.name)
    if self.alt:
      names.append(self.alt)
    if self.reg:
      for name in names:
        regcmd(name, '%s/%s' % (self.BLOCK_PREFIX, self.name), self.desc)

    return self
        
  def concommand(self):
    command, argv, args, exp = escompile(getargv(0), map(getargv, xrange(1, getargc())), getargs())
    line = (None, command, argv, args, exp)
    stack.queue([line], 'console', priority=True)
    sv.save()
    
  def run(self, argv, args, exp):
      
    if self.minargs and len(argv) < self.minargs:
      raise SyntaxError
      
    if exp:
      argv = expand(argv, exp)
      args = None
      
    if not self.AUTOCREATE:
      for varname in map(argv.__getitem__, self.vars):
        if not sv.exists(varname):
          raise NameError, ('var', varname)
      
    _args = {}
      
    if self.argv:
      _args['argv'] = argv
      
    if self.args:
      if not args:
        if self.remquotes:
          args = ' '.join(map(str, argv[self.argsfrom:]))
        elif exp and self.argsfrom or not self.argv:
          args = join(argv[self.argsfrom:])
      _args['args'] = args
      
    self.method(**_args)
    


from ..cmds import addons, conditions, comp, expansion, install, keygroups, maths, \
  misc, output, players, reference, sounds, time, run, usercommands, vars, vectors, voodoo
