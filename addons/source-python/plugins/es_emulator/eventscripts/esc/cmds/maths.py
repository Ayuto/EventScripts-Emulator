import es
from random import randint
from math import sin, cos, tan, asin, acos, atan
from operator import add, sub, mul, pow, truediv as div
from ..val import sv, STR, INT, NUM, VAR, ANY
from . import Command

root = lambda a, b: pow(a, 1.0/b)

# https://stackoverflow.com/a/14246007
def correct(value, bits, signed):
    base = 1 << bits
    value %= base
    return value - base if signed and value.bit_length() == bits else value

byte, sbyte, word, sword, dword, sdword, qword, sqword = (
    lambda v: correct(v, 8, False), lambda v: correct(v, 8, True),
    lambda v: correct(v, 16, False), lambda v: correct(v, 16, True),
    lambda v: correct(v, 32, False), lambda v: correct(v, 32, True),
    lambda v: correct(v, 64, False), lambda v: correct(v, 64, True)
)

def emulate_datatype_overflow(value):
    # int?
    if int(value) == value:
        # Emulate a signed int
        return sdword(value)
    
    # TODO: Handle float overflow
    return value

_math_operators = {
  '+': add, 'add': add,
  '-': sub, 'subract': sub,
  '*': mul, 'multiply': mul,
  '/': div, 'divide': div,
  '^': pow, 'power': pow,
  '//': root, 'root': root,
}

_math_functions = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'abs', 'int', 'float']

@Command(syntax='<variable> <operator> [value]', types=(VAR, STR, ANY), desc='EventScripts math functions, courtesy of Cr3V3TT3')
def math(argv):
  var, op = argv[:2]
  val = sv[var]
  if val.isstring():
    raise ValueError('math function called on a non-numeric value: %s, %s' % (var, val.strval))
  val = emulate_datatype_overflow(NUM(val))
  if op in _math_operators:
    if len(argv) < 3:
      raise SyntaxError
    val2 = argv[2]
    if val2.isstring():
      raise ValueError('math function called on a non-numeric value: %s' % val2.strval)
    sv[argv[0]] = emulate_datatype_overflow(
        _math_operators[op](val, emulate_datatype_overflow(NUM(val2))))
  elif op in _math_functions:
    sv[argv[0]] = emulate_datatype_overflow(eval(op)(val))
  else:
    raise SyntaxError('bad operation "%s"' % op)
  
@Command(syntax='<cvar> <minimum> <maximum>', types=(VAR, INT, INT), desc='Place a random value between <minimum> and <maximum> to <cvar>')
def rand(argv):
  sv[argv[0]] = randint(*sorted(argv[1:3]))
  
@Command(syntax='<var> <math-expression>', types=VAR, desc='Adds a say command that refers to a particular block.')
def mathparse(argv):
  del sv[argv[0]]
  es.mathparse(argv[0], argv[1])
