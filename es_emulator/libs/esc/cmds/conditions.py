import es, esc
from .. import commands, stack
from ..parse import tokenize, expcompile, expand, getexpindices, coerce
from ..val import sv, STR, ANY, OP
from . import Command

class While(object):
  
  def __init__(self, rawcond):
    self.tokens = expcompile(tokenize(rawcond))[:3]
    self.exp = getexpindices(self.tokens)
    coerce(self.tokens, (ANY, OP, ANY), self.exp)
    
    if len(self.tokens) < 3:
      raise SyntaxError, 'invalid condition'
      
    if not self.tokens[1]:
      raise SyntaxError, 'invalid conditional operator'
             
  def eval(self):
    one, op, two = expand(self.tokens, self.exp)
    return op(one, two)
  
@Command(syntax='(<value> <operator> <value>) <do/then> [[commandstring]]', expand=True, pre=False, argsfrom=7, alt='es_xif', types=(STR, ANY, OP, ANY), desc='Allows you to conditionalize a script line.')
def _if(argv, args):
  lb, one, op, two, rb, qualifier = argv[:6]
  if lb != '(' or rb != ')' or qualifier not in ('then', 'do'):
    raise SyntaxError
  if not op:
    raise SyntaxError, 'invalid conditional operator'
  result = op(one, two)
  stack.setcond(bool(result))
  if result and qualifier == 'then':
    if len(argv) > 6:
      stack.insertline(argv[6], argv[7:], args)

@Command(syntax='<operator>(<value>) <do>', pre=False, expand=False, desc='ifx <mode>(<arguments>) do\nNever supports expansion of variables.')
def ifx(argv):
  op, lb, val, rb, qualifier = argv[:5]
  if lb != '(' or rb != ')' or qualifier != 'do':
    raise SyntaxError
  op = op.lower()
  if not op in ('true', 'false', 'parse'):
    raise SyntaxError, 'invalid conditional operator'
  if op in ('true', 'false'):
    result = sv.bool(val)
    if op == 'false':
      result = not result
  else:
    del sv['_tempcoreesc']
    es.set('_tempcoreesc', 0)
    es.mathparse('_tempcoreesc', val)
    result = sv._tempcoreesc
  stack.setcond(bool(result))
  
@Command(expand=True, pre=False, argsfrom=1, alt='es_xelse', syntax='<commandstring>', desc='else <any typical script line>\nExecutes the line if the previous \'if\' call returned false.')
def _else(argv, args):
  prevcond = stack.loopstack[-1][0]
  if not prevcond is None:
    stack.setcond(not prevcond)
  if argv[0] != 'do' and not prevcond:
    stack.insertline(argv[0], argv[1:], args)
    
@Command(pre=False, expand=False, syntax='<condition> <commandstring>', desc='While loop')
def _while(argv):
  stack.setwhile(While(argv[0]))
  if argv[1] != 'do':
    stack.insertrawblock(argv[1])
