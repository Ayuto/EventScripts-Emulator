# -*- coding: utf-8 -*-

addons   = {}
commands = {}
aliases  = {}

class Stack(object):
  
  EMPTYLOOP = [None] * 3
  EMPTYARGS = {'argv': [], 'args': '', 'uid': 0}
  
  codestack =   []
  loopstack =   [EMPTYLOOP]
  argstack =    [EMPTYARGS]
  
  newcode =     False
  die =         False
  
  def queue(self, code, blockname, priority=False, userargs=None): # Queues code and sets it running
  
    codestack = self.codestack
    argstack = self.argstack
    
    self.scripttrace = sv.eventscripts_scripttrace # TODO: Something about this
    
    codestack.append((blockname, deque(code), priority))
    if not priority:
      self.loopstack.append(self.EMPTYLOOP)
    argstack.append(userargs or argstack[-1])

    if priority or len(codestack) == 1:
      self.run()
    else:
      self.newcode = True
      
  def queueline(self, command, argv, args, blockname, priority=False):
    command, argv, args, exp = escompile(command, list(argv), args)
    self.queue([(self.currentline, command, argv, args, exp)], blockname, priority)
      
  def insertrawline(self, line):
    self.insertlines(list(getcommands(line, self.currentline)))
    
  def insertrawlines(self, lines):
    map(self.insertrawline, reversed(lines))
      
  def insertline(self, command, argv, args=None, n=None):
    command, argv, args, exp = escompile(command, list(argv), args)
    self.currentblock.appendleft((n or self.currentline, command, argv, args, exp))
    
  def insertlines(self, lines):
    map(self.currentblock.appendleft, reversed(list(lines)))
    
  def insertblock(self, block):
    self.currentblock.appendleft(block)
    
  def insertrawblock(self, code):
    self.insertblock(getcode(code, self.currentline))
    
  def runall(self):
    while self.codestack:
      self.run()
  
  def run(self): # Runs code stack
  
    if self.die: return # TODO: Remove, for debugging.
  
    codestack = self.codestack
    loopstack = self.loopstack
    argstack  = self.argstack
    
    while codestack:
      
      blockname, block, priority = codestack[-1]
        
      while block:
        
        self.currentblockname, self.currentblock = blockname, block
        subblock = block[0]
        
        if type(subblock) is list: # New subblock
        
          lastcond, lastwhile, lastfor = loopstack[-1]
        
          if lastcond is False:
            block.popleft()
            self.setcond()
            continue
            
          else:
            
            if lastwhile:
              if not lastwhile.eval():
                block.popleft()
                self.setwhile()
                continue
              
            elif lastfor:
              variable, items = lastfor
              if items:
                sv[variable] = items.pop(0)
              else:
                block.popleft()
                self.setfor()
                continue
              
            else:
              block.popleft()
              
            codestack.append((blockname, deque(subblock), False))
            argstack.append(argstack[-1])
            loopstack.append(self.EMPTYLOOP)
            break

        else: # Ordinary code line
        
          self.currentline, command, argv, args, exp = block.popleft()
          
          self.command(command, argv, args, exp)
          
          if self.die:
            sv.save()
            return
          
          if self.newcode: # We've had some new code queued, so break the block loop and start running it
            self.newcode = False
            break # TODO: some tail call optimisation -- pop the stack in queue() if currentblock is empty
          
      else:
        codestack.pop()
        argstack.pop()
        if priority:
          return
        else:
          loopstack.pop()
          
  def getargv(self, n):
    userargs = self.argstack[-1]
    if userargs and n <= len(userargs['argv']):
      return userargs['argv'][n-1] if n else userargs['cmdname']
    return ''
    
  def getargs(self):
    userargs = self.argstack[-1]
    args = userargs['args'] if userargs else ''
    if args is None:
      return join(userargs['argv'])
    return args
    
  def getargc(self):
    userargs = self.argstack[-1]
    return len(userargs['argv']) + 1 if userargs else 0
    
  def getcmduserid(self):
    userargs = self.argstack[-1]
    return userargs['uid'] if userargs else 0
          
  def kill(self):
    self.die = True
    
  def trace(self, cmdname, args):
    if self.scripttrace:
      level = len(self.codestack) - 1
      args = args or ''
      line = '%s %s' % (cmdname, args)
      n = ' %s' % self.currentline if self.currentline else ''
      block = ' [%s%s]' % (self.currentblockname, n)
      dbgmsg(0, ('>> %s%s' % ('  ' * level, line)).ljust(50) + block)
    
  def setcond(self, status=None):
    self.loopstack[-1] = [status, None, None]
    
  def setwhile(self, condition=None):
     self.loopstack[-1] = [None, condition, None]
     
  def setfor(self, *info):
     self.loopstack[-1] = [None, None, info]
     
  def command(self, command, argv=None, args=None, exp=None): # TODO: GenericCommand object for all of those unknowns - then this method can be scrapped?
    
    self.trace(command, args or join(argv))
    commandname = command
    
    try:
      
      if isinstance(command, Command):
        commandname = command.expname
        command.run(argv, args, exp)
        
      else:
        
        cmdblock = queryregcmd(command)
        block = splitblock(cmdblock) if cmdblock else None
        if block and blockexists(*block):
          addons[block[0]].blocks[block[1]].run(userargs={'cmdname': command, 'argv': argv, 'args': args, 'uid': 0})
          
        elif command in aliases:
          return aliases[command].run()
            
        elif exists('command', command) or sv.exists(command):
          if args is None:
            args = join(argv)
          sv.save()
          ForceServerCommand('%s %s' % (command, args))
            
        else:
          raise NameError, ('command', command)
          
    except SyntaxError, e: # TODO: Custom errors
      if not e.msg:
        self.error(commandname, 'Syntax: %s %s' % (command.expname, self.syntax))
      else:
        self.error(commandname, e)
      
    except NameError, e:
      print e
      print commandname
      self.error(commandname, 'The %s \'%s\' could not be found' % e.args)
      
    except (ValueError, IOError, RuntimeError), e:
      self.error(commandname, e)
        
  def error(self, commandname, error):
    n = self.currentline
    dbgmsg(0, '[%s%s] %s: %s' % (self.currentblockname, ' %s' % n if n else '', commandname, error))

stack = Stack()

import monkeypatch # TODO: nuke

from collections import deque
from es import exists, queryregcmd, ForceServerCommand, dbgmsg
from .parse import join, splitblock, getcommands, getcode, escompile
from .val import sv
from .interface import blockexists
from .cmds import Command
