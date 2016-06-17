import es

_variables = {}

def increment(variable, silent=False):
	"""
	Increases the reference count of a variable by one.
	"""
	name = variable.getName()
	count = 1
	if name in _variables:
		_variables[name]["count"] += 1
		count = _variables[name]["count"]
	else:
		_variables[name]["count"] = 1
		_variables[name]["oldValue"] = str(variable)

	if silent:
		es.forcevalue(name, 1)
	else:
		variable.set(1)

	es.dbgmsg(1, 'refcount: Variable "%s" has a reference count of "%d".' % (name, count))

def decrement(variable, silent=False):
	"""
	Decreases the reference count of a variable by one.
	"""
	name = variable.getName()
	if name not in _variables:
		raise ReferenceError(name + " has a reference count of 0.")

	# Decrease the reference count for the variable.
	_variables[name]["count"] -= 1
	count = _variables[name]["count"]
	if 0 == count:
		if silent:
			es.forcevalue(name, _variables[name]["oldValue"])
		else:
			variable.set(_variables[name]["oldValue"])
		del _variables[name]

	es.dbgmsg(1, 'refcount: Variable "%s" has a reference count of "%d".' % (name, count))

def count(variable):
	"""
	Returns the reference count of a variable.
	"""
	name = variable.getName()
	if name in _variables:
		return _variables[name]["count"]
	return 0
