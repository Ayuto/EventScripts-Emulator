'''
This module provides access to the KeyValues object which is used to
provide full recursive access to Valve's KeyValues C++ class and file format.
'''
import es

types={}
types[0] = "TYPE_NONE"
types[1] = "TYPE_STRING"
types[2] = "TYPE_INT"
types[3] = "TYPE_FLOAT"
types[4] = "TYPE_PTR"
types[5] = "TYPE_WSTRING"
types[6] = "TYPE_COLOR"
types[7] = "TYPE_NUMTYPES"


def getKeyGroup(name):
    '''
    Returns a KeyValues class for a keygroup created with es.keygroupcreate.
    '''
    x = es.keygroupgetpointer(name)
    if x is not None and x != 0:
        k = KeyValues(existingid=x)
        k._parent_ = 0
        return k
    else:
        return None

class KeyValues(object):
    '''
    This is a wrapper class for Valve's C++ KeyValues class. It is basically a
    tree-based datastructure where every node has a name and a value.
    See http://developer.valvesoftware.com/wiki/KeyValues_class for more info
    on Valve's KeyValues C++ class.
    '''
    _id_ = 0
    _parent_ = None
    def __init__(self, name=None, parent=None, existingid=None, filename=None):
        '''
        You can create a new KeyValues object by passing in different
        combinations of arguments:
        With only an existingid, KeyValues returns a wrapper around that
        existing id (i.e. C++ pointer). With only a parent, we'll create a
        new randomly named subkey. With a parent and name, we'll find/make a
        subkey of that name. With a name only, we'll create an unparented key
        with that name. With a filename, we'll load the KeyValues tree from
        disk and return it as the parent.
        '''
        if existingid is not None:
            #print "kv", existingid, parent
            self._id_ = existingid
            self._parent_ = parent
        else:
            if parent is None:
                self._id_ = es.keypcreate()
                if filename is not None:
                    self.load(filename)
                if name is not None:
                    es.keypsetname(self._id_, str(name))
            else:
                self._parent_ = parent
                if name is None:
                    self._id_ = es.keypcreatesubkey(parent._id_)
                else:
                    self._id_ = es.keypfindsubkey(parent._id_, str(name))
    def load(self, filename):
        '''
        Loads this KeyValue's contents from a file.
        '''
        es.keyploadfromfile(self._id_, filename)
    def save(self, filename):
        '''
        Saves this KeyValue's contents from a file.
        '''
        es.keypsavetofile(self._id_, filename)
    def getParent(self):
        '''
        Returns the parent KeyValues class to this one.
        '''
        return self._parent_
    def setParent(self, parent):
        '''
        Attached this key in Python to the other KeyValues. Not recommended to
        be used externally to the class.
        '''
        self._parent_ = parent
    def detachParent(self):
        '''
        Detach this KeyValues key from it's parent KeyValues class.
        '''
        if isinstance(self._parent_, KeyValues):
            if self._id_ > 0 and self._parent_._id_ > 0:
                es.keypdetachsubkey(self._parent_._id_, self._id_)
            self._parent_ = None
    def keys(self):
        '''
        Returns a list of top-level subkeys.
        '''
        keyers = []
        for i in self:
            keyers.append(i.getName())
        return keyers
    def __del__(self):
        if self._id_ > 0 and self._parent_ is None:
            es.keypdelete(self._id_)
    def __str__(self):
        return es.keypgetname(self._id_)
    def __hash__(self):
        return self._id_
    def __contains__(self, item):
        if str(item) in list(self.keys()):
            return True
        else:
            return False
    def __getitem__(self, name):
        '''
        Look up a value by name, a lot like a dictionary. Can return a value
        or a subkey, depending on what is returned.
        '''
        x = es.keypfindsubkey(self._id_, str(name), False)
        if x is None or x == 0:
            raise KeyError(f"{name} not found in keyvalues object")
        else:
            typ = es.keypgetdatatype(x)
            if types[typ] == "TYPE_NONE":
                return KeyValues(parent=self, existingid=x)
            elif types[typ] == "TYPE_STRING" or types[typ] == "TYPE_WSTRING":
                return es.keypgetstring(self._id_, str(name))
            elif types[typ] == "TYPE_INT":
                return es.keypgetint(self._id_, str(name))
            elif types[typ] == "TYPE_FLOAT":
                return es.keypgetfloat(self._id_, str(name))
##          types[4] = "TYPE_PTR"
##          types[6] = "TYPE_COLOR"
##          types[7] = "TYPE_NUMTYPES"
            else:
                raise NotImplemented(f"KeyValues does not yet support type: {types[typ]}")
    def __setitem__(self, name, value):
        '''
        Stores a name/value pair in the keygroup. Only ints, floats, strings,
        and KeyValues classes (as subkeys) can be stored.
        '''
        if (isinstance(value, KeyValues)):
            x = es.keypfindsubkey(self._id_, str(name), True)
            if x:
                es.keyprecursivekeycopy(x, value._id_)
        else:
            if (isinstance(value, int)):
                es.keypsetint(self._id_, str(name), value)
            elif (isinstance(value, float)):
                es.keypsetfloat(self._id_, str(name), value)
            else:
                es.keypsetstring(self._id_, str(name), str(value))
    def __delitem__(self, name):
        '''
        Delete a subkey from the keygroup.
        '''
        x = es.keypfindsubkey(self._id_, str(name), False)
        if x is None or x == 0:
            raise KeyError(f"{name} not found in keyvalues object")
        else:
            k = KeyValues(parent=self, existingid=x)
            k.detachParent()
    def getName(self):
        return es.keypgetname(self._id_)
    def getString(self, var=""):
        return es.keypgetstring(self._id_, var)
    def getInt(self, var):
        return es.keypgetint(self._id_, var)
    def getFloat(self, var):
        return es.keypgetfloat(self._id_, var)
    class KeyValuesIter(object):
        def __init__(self, currentkey):
            self.nextkeyid = currentkey._id_
            self.parent = currentkey
        def __iter__(self):
            return self
        def __next__(self):
            if self.nextkeyid == self.parent._id_:
                self.nextkeyid = es.keypgetfirstsubkey(self.nextkeyid)
            else:
                self.nextkeyid = es.keypgetnextkey(self.nextkeyid)
            if self.nextkeyid is None or self.nextkeyid == 0:
                raise StopIteration
            return KeyValues(existingid=self.nextkeyid, parent=self.parent)
    def __iter__(self):
        return self.KeyValuesIter(self)

