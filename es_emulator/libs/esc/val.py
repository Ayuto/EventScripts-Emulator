# -*- coding: utf-8 -*-

from re import compile
from operator import eq, ne, lt, le, gt, ge
from es import exists, getString, getInt, getFloat, setString, getCurrentEventVarString, getFlags

_operators = {
  '==': '==', '=': '==', 'equalto': '==',
  '!=': '!=', '!==': '!=', 'notequalto': '!=',
  '>': '>', 'greaterthan': '>',
  '<': '<', 'lessthan': '<',
  '>=': '>=', '=>': '>=', 'notlessthan': '>=', 
  '<=': '<=', '=<': '<=', 'notgreaterthan': '<=', 
  'in': 'in', 'notin': 'notin',
  '~~': '~~', 'approx': '~~',
  '!~': '!~', 'notapprox': '!~',
}

def esctype(function):
  def _type(value):
    if not isinstance(value, Val):
      value = Val(value)
    return function(value)
  return _type
  
def STR(value):
  return str(value)
  
def VAR(value):
  return str(value)
  
def OP(value):
  if value in _operators:
    return _functions[_operators[value]]
  print "WAKAWAKAWAKA", value
  
@esctype
def ANY(value):
  return value
  
@esctype
def INT(value):
  return int(value)
  
@esctype
def FLOAT(value):
  return float(value)
  
@esctype
def NUM(value):
  return value.number()

class Val(object):
  
  __slots__ = ['strval', 'intval', 'floatval', 'nonzero']
  
  protected = False
  
  def __init__(self, strval):
    self.strval = str(strval)
    
  def initialize(self):
    
    try:
      self.floatval = float(self.strval)
      self.intval = int(self.floatval)
      self.nonzero = bool(self.floatval)
    except ValueError:
      self.floatval = 0.0
      self.intval = 0
      self.nonzero = bool(self.strval)
    
  def __getattr__(self, name):
    self.initialize()
    return getattr(self, name)
    
  def __repr__(self):
    return repr(str(self))
        
  def __str__(self):
    return self.strval
    
  def isstring(self):
    return (not float(self)) and (bool(self) or not self.strval)
    
  def count(self, substr):
    return self.strval.count(substr)
    
  def split(self, substr):
    return self.strval.split(substr)
    
  def strip(self):
    return self.strval.strip()
    
  def replace(self, search, replace, n=-1):
    return self.strval.replace(str(search), str(replace), n)
    
  def __getitem__(self, item):
    return self.strval[item]
  
  def __nonzero__(self):
    return self.nonzero
  
  def __int__(self):
    return self.intval
  
  def __float__(self):
    return self.floatval
  
  def number(self):
    return self.intval if self.intval == self.floatval else self.floatval
    
  def __hash__(self):
    return hash(self.strval)
    
  def __eq__(self, other):
    if float(self):
      return float(self) == float(other)
    if not self.protected and not bool(self):
      return not bool(other)
    return str(self) == str(other)
    
  def __ne__(self, other):
    if float(self):
      return float(self) != float(other)
    if not self.protected and not bool(self):
      return bool(other)
    return str(self) != str(other)
    
  def __lt__(self, other):
    return float(self) < float(other)
    
  def __le__(self, other):
    return float(self) <= float(other)
    
  def __gt__(self, other):
    return float(self) > float(other)
    
  def __ge__(self, other):
    return float(self) >= float(other)
    
  def isin(self, other):
    return str(self) in str(other)

  def notin(self, other):
    return str(self) not in str(other)
    
  def approx(self, other):
    return round(float(self), 6) == round(float(other), 6)
    
  def notapprox(self, other):
    return round(float(self), 6) != round(float(other), 6)
    
    
_functions = {
  '==': eq, '!=': ne,
  'in': Val.isin, 'notin': Val.notin,
  '>': gt, '<': lt,
  '<=': le, '>=': ge,
  '~~': Val.approx, '!~': Val.notapprox,
}


class ServerVal(Val):
  
  def __init__(self, strval, protected=False):
    self.strval = str(strval)
    self.initialize()
    if protected:
      self.protected = True
      self.expanded = '(protected)'
    elif not self.nonzero:
      self.expanded = '0'
    else:
      self.expanded = str(self.number() or self.strval.replace('"', '`'))
    
  def __str__(self):
    return self.expanded
    
class EventVal(ServerVal):
  
  def __init__(self, strval, protected=False):
    self.strval = str(strval)
    self.initialize()
    self.expanded = self.strval.replace('"', '`')

class Sv(object):
  
  valtype = ServerVal
  expand = getString
  varcache = {}
  
  def __setitem__(self, var, value):
    var, value = str(var), str(value)
    result = self.varcache[var] = self.valtype(value)
    setString(var, value)
      
  def __contains__(self, var):
    return var in self.varcache
      
  def __delitem__(self, var):
    if var in self.varcache:
      del self.varcache[var]
      
  def  __getitem__(self, var):
    var = str(var)
    if var in self.varcache:
      return self.varcache[var]
    value = self.varcache[var] = self.valtype(self.expand(var), protected=(getFlags(var) or 0) & 32) # TODO: keep an eye on es_flags
    return value
    
  def __call__(self, var):
    return self[var].strval
    
  def __getattr__(self, var):
    return bool(self[var])
    
  bool = __getattr__

  def save(self):
    self.varcache.clear()
    
  def exists(self, var):
    var = str(var)
    return var in self.varcache or exists('variable', var)
    
sv = Sv()

class Ev(Sv):
  valtype = EventVal
  expand = getCurrentEventVarString

ev = Ev()
