import es

_addons = {}

def increment(addon):
	"""
	Increases the reference count of an addon by one.
	"""
	count = 1
	if addon in _addons:
		_addons[addon]["count"] += 1
		count = _addons[addon]["count"]
	else:
		_addons[addon]["count"] = 1
		es.createscriptlist("_refcount_scripts")
		_addons[addon]["oldValue"] = es.exists("key", "_refcount_scripts", addon)
		es.keygroupdelete("_refcount_scripts")

	# Load the addon.
	es.load(addon)

	es.dbgmsg(1, 'refcount: Addon "%s" has a reference count of "%d".' % (addon, count))

def decrement(variable, silent=False):
	"""
	Decreases the reference count of an addon by one.
	"""
	if addon not in _addons:
		raise ReferenceError(name + " has a reference count of 0.")

	# Decrease the reference count for the addon.
	_addons[addon]["count"] -= 1
	count = _addons[addon]["count"]
	if 0 == count:
		es.unload(addon)
		del _addons[name]
	else:
		es.load(addon)

	es.dbgmsg(1, 'refcount: Addon "%s" has a reference count of "%d".' % (addon, count))

def count(addon):
	"""
	Returns the reference count of an addon.
	"""
	if addon in _variables:
		return _addons[addon]["count"]
	return 0
