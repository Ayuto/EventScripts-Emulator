# -*- coding: utf-8 -*-

import re
from . import commands
from .val import sv, ev, Val, STR

# Split addon into hierarchical blocks and events, with separated and tokenized commands. Slightly voodoo, but written to be fast and non mem intensive.

BLOCK_START_CHAR = '{'
BLOCK_END_CHAR = '}'
BLOCK_TYPES = ('block', 'event')
_blockname_regex = re.compile('^(%s) +([^ ]+)' % '|'.join(map(re.escape, BLOCK_TYPES)))

def splitblocks(file):
  
  # Container dict for script, in form {blocktype: {blockname: [lines, of, code, and, [subblocks, with, more, code]]}}
  script = dict((blocktype, dict()) for blocktype in BLOCK_TYPES)
  
  blockstack = []       # A hierarchical stack of pointers to locations in the current block e.g. [block, subblock1, subblock2 ...]
  potentialblock = None # The block which is potentially about to be currentblock given a BLOCK_START_CHAR
  
  for n, line in enumerate(file):
    
    n += 1
    line = line.strip()
    if line:
      
      if potentialblock: # We've had a block descriptor and are waiting for BLOCK_START_CHAR to start a new block. Anything else will reset the search.
        
        if line.startswith(BLOCK_START_CHAR):
          currentblock = script[potentialblock[0]][potentialblock[1]] = []
          blockstack.append(currentblock)
          potentialblock = None
          continue
          
        else:
          potentialblock = None
        
      if not blockstack: # We're waiting for a block descriptor, e.g. block rinse_and_repeat
      
        blockmatch = _blockname_regex.match(line) # Does it look like a block?
        if blockmatch:
          potentialblock = blockmatch.groups()  # (blocktype, blockname)
        
      else: # We're in a block
        
        if line.startswith(BLOCK_START_CHAR): # Move up a level and start a new subblock
        
          newsubblock = []
          currentblock.append(newsubblock)
          currentblock = newsubblock
          blockstack.append(newsubblock)
          
        elif line.startswith(BLOCK_END_CHAR): # Move down a level and remove subblock from stack
        
          blockstack.pop()
          if blockstack:
            currentblock = blockstack[-1]
            
        else: # Tokenize line and add it to current subblock
        
          map(currentblock.append, getcommands(line, n))
            
  return script
  

def getcode(line, n): # TODO: reexamine
  return list(getcommands(line, n))
  
TOKENCHARS = "'():;{}"
_remcomment_regex = re.compile('"[^"]*"|(//)').finditer
_tokenize_regex = re.compile('"[^"]*"|[%s]|[^%s ]+' % (TOKENCHARS, TOKENCHARS))
  
def getcommands(line, n):
  
  if line.count('"') % 2 == 1:
    line += '"'
    
  for match in _remcomment_regex(line):
    if match.group(1):
      line = line[:match.start()].rstrip()
      break
  
  tokens = _tokenize_regex.finditer(line)
  fin = False
  while tokens:
    command = tokens.next()
    start = end = command.end()
    command = command.group()
    if command == ';':
      continue
    argv = []
    for token in tokens:
      value = token.group()
      if value == ';':
        break
      argv.append(value.replace('"', ''))
      end = token.end()
    else:
      fin = True
    command, argv, args, exp = escompile(command.replace('"', ''), argv, line[start:end].lstrip())
    yield (n, command, argv, args, exp)
    if fin:
      break
    
def escompile(commandname, argv, args=None): # TODO: keep as strings until needed to be something else?
  exp = None
  if commandname in commands:
    command = None
    if commandname == 'es' and argv and argv[0] in commands:
      newcommand = commands[argv[0]]
      if newcommand.expand and argv[0] == newcommand.expname:
        command = newcommand
        argv.pop(0)
        expand = True
    if not command:
      command = commands[commandname]
      expand = command.expand and commandname == command.expname
    if expand:
      argv = expcompile(argv)
      exp = getexpindices(argv)
    coerce(argv, command.types, exp)
    if command.args:
      if exp:
        if exp[-1] < command.argsfrom:
          args = join(argv[command.argsfrom:])
      elif args is not None:
        args = argsfrom(args, command.argsfrom)
    else:
      args = None
  else:
    command = commandname
  return command, tuple(argv), args, exp
  
def coerce(tokens, types, exp):
  for n, (token, newtype) in enumerate(map(None, tokens, types)):
    if token:
      if exp and n in exp:
        token.append(newtype or STR)
      elif newtype:
        tokens[n] = newtype(token)
  
  

  
# Split line into tokens a la source console


    
def tokenize(line):
  return [match.replace('"', '') for match in _tokenize_regex.findall(line)]

  
# Joins separated tokens into commandstring, complete with quote marks where necessary to avoid future tokenization. Only use where necessary.


_escapechars_regex = re.compile('[;%s]' % re.escape(''.join(sorted(sv('eventscripts_escapechars')))))

def join(tokens):
  return ' '.join('"%s"' % token if not token or (_escapechars_regex.search(token) and (len(token) > 1 or token == ';')) else token for token in map(str, tokens))


# Get arguments as a string

_args_regex = re.compile('("[^"]*"|[%s]|[^%s ]+) *' % (TOKENCHARS, TOKENCHARS))

def getargs(line):
  return line[_args_regex.match(line).end():]
  
  
# Get arguments as a string from a given index


ARGSFROM_REGEX = '(("[^"]*"|[%s]|[^%s ]+) *){%%s}' % (TOKENCHARS, TOKENCHARS)

def argsfrom(args, index):
  match = re.match(ARGSFROM_REGEX % index, args)
  return args[match.end():].replace('"', '') if match else ''
    
SV_OPERATOR = 'server_var'
EV_OPERATOR = 'event_var'
VAR_LEFT_DELIM = '('
VAR_RIGHT_DELIM = ')'
OP_CLASS = {
  SV_OPERATOR: sv,
  EV_OPERATOR: ev,
}
VAR_DELIM_CLASS = (VAR_LEFT_DELIM, VAR_RIGHT_DELIM)

def expcompile(tokens):
  index = len(tokens)
  if index > 3 and SV_OPERATOR in tokens or EV_OPERATOR in tokens:
    index -= 3
    available = 3
    while index:
      index -= 1
      available += 1
      if available >= 4:
        op, ob, var, cb = tokens[index:index+4]
        if op in OP_CLASS and (ob, cb) == VAR_DELIM_CLASS:
          if not type(var) is list:
            var = [var]
          var.append(OP_CLASS[op])
          tokens[index:index+4] = [var]
          available -= 3
  return tokens
  
def getexpindices(tokens):
  return tuple(n for n, token in enumerate(tokens) if isinstance(token, list)) or None
  
def expand(tokens, exp):
  if exp:
    tokens = list(tokens)
    for index in exp:
      token = tokens[index]
      token, exporder, newtype = token[0], token[1:-1], token[-1]
      for exptype in exporder:
        if token == '_randtoken_tstring': pass
        token = exptype[token]
      tokens[index] = newtype(token)
  return tokens
  
def splitblock(path):
  if not '/' in path:
    return None
  addon, null, block = cleanpath(path).rpartition('/')
  return (addon, block)
  
# Cleans up addon paths that look//like\this

def cleanpath(path):
  path = path.replace('\\', '/')
  while '//' in path:
    path = path.replace('//', '/')
  return path
