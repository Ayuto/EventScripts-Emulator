import math

#plugin information
"""
info = {}
info['name'] = "Vecmath EventScripts python library"
info['version'] = "2.1.7"
info['author'] = "GODJonez"
info['url'] = "http://python.eventscripts.com/pages/Vecmath/"
info['description'] = "Provides class and functions for handling vectors for Source"
info['tags'] = ""
"""

def nullseq(sequences):
    '''
Converts a list of iterables such that they become lists with as many
items as is in the longest list by appending extra 0 items to them.
    '''
    maxlen = max((len(x) for x in sequences))
    for x in sequences:
        l = maxlen - len(x)
        yield list(x) + [0]*l
    
def nullzip(*sequences):
    '''
The same as built-in zip function except instead of truncating
to the shortest sequence, zeroes are added to respect the length of the longest
sequence.
    '''
    return list(zip(*nullseq(sequences)))

class Vector(object):
    '''
Spatial Vector in Cartesian space.

Creating a new vector can be done in one of the following ways:
    - passing a sequence of numbers:
        myvec = vecmath.Vector( [1, 2, 3] )
    - passing numbers as separate arguments:
        myvec = vecmath.Vector(1, 2, 3)
    - passing so called "vectorstring":
        myvec = vecmath.Vector("1.000000,2.000000,3.000000")
    - passing Source entity Keyvalues vector value:
        myvec = vecmath.Vector("1.000000 2.000000 3.000000")

The first three values can be overridden with keyword arguments x, y and z:
    myvec = vecmath.Vector(sequence, x=500)
    myvec = vecmath.Vector(sequence, y=-2.7, z=0, x=42)
    '''
    
    def __init__(self, *args, **kw):
        '''
Initializes a new Vector instance, see class documentation for info.
        '''
        if len(args) > 1:
            self.vl = [float(x) for x in args]
        elif len(args) == 1:
            vl = args[0]
            if type(vl).__name__ == 'generator':
                vl = tuple(vl)
            try:
                self.vl = [float(x) for x in vl]
            except ValueError:
                self.vl = [float(x) for x in vl.replace(' ', ',').split(",")]
            except TypeError:
                raise TypeError(f"Invalid data type {type(vl).__name__} ({v1}) for vector.")
        else:
            self.vl = [0,0,0]
        if kw:
            try:
                compval = 0
                for comp in ('x','y','z'):
                    if comp in kw:
                        self.vl[compval] = float(kw[comp])
                    compval += 1
            except:
                raise TypeError(f"Invalid data type {type(kw[comp]).__name__} ({kw[comp]}) in override for vector.")
    
    def __repr__(self):
        ''' Returns a string representation of itself. '''
        return f"Vector({self.vl})"
    
    def __list__(self):
        ''' Converts the vector into a list. '''
        return list(self.vl)
    
    def getdict(self):
        '''
Converts the vector into a dictionary with at most three components.

By convention these components are named "x", "y" and "z",
if the vector has more components, the rest are discarded,
if the vector has less components, then items from the dictionary are omitted.
        '''
        return dict(list(zip("xyz", self.vl)))
    
    def __str__(self):
        '''
Returns the vector info as a vectorstring.

An example return value is "0.000000,0.000000,0.000000"
        '''
        return self.getstr()
    
    def getstr(self,sep=","):
        '''
Returns a string representation of the vector with specified separator.

By default the separator is "," to produce a vectorstring
"0.000000,0.000000,0.000000", but can be changed to be any string.
        '''
        return sep.join(('%0.6f'%v for v in self.vl))
    
    def __len__(self):
        ''' Returns the dimension of the vector (i.e. the number of components). '''
        return len(self.vl)
    
    def __add__(self, vl2):
        '''
Adds two vectors mathematically.

If the vectors are not of the same dimension, the lesser dimensioned vector
is assumed to have values of zero for the missing dimensions.

The simplified formula of vector addition is:
vector1 + vector2 == (x1, y1, z1) + (x2, y2, z2) = (x1 + x2, y1 + y2, z1 + z2)
        '''
        return Vector(((x+y) for x,y in nullzip(self,vl2)))
    
    def __iadd__(self, vl2):
        '''
Adds another vector to this one mathematically.

If the vectors are not of the same dimension, the lesser dimensioned vector
is assumed to have values of zero for the missing dimensions.

The simplified formula of vector addition is:
vector1 + vector2 == (x1, y1, z1) + (x2, y2, z2) = (x1 + x2, y1 + y2, z1 + z2)
        '''
        self.vl = [(x+y) for x,y in nullzip(self,vl2)]
        return self
    
    def __sub__(self, vl2):
        '''
Subtracts two vectors mathematically.

If the vectors are not of the same dimension, the lesser dimensioned vector
is assumed to have values of zero for the missing dimensions.

The simplified formula of vector subtraction is:
vector1 - vector2 == (x1, y1, z1) - (x2, y2, z2) = (x1 - x2, y1 - y2, z1 - z2)
        '''        
        return Vector(((x-y) for x,y in nullzip(self,vl2)))
    
    def __isub__(self, vl2):
        '''
Subtracts another vectors from this one mathematically.

If the vectors are not of the same dimension, the lesser dimensioned vector
is assumed to have values of zero for the missing dimensions.

The simplified formula of vector subtraction is:
vector1 - vector2 == (x1, y1, z1) - (x2, y2, z2) = (x1 - x2, y1 - y2, z1 - z2)
        '''        
        self.vl = [(x-y) for x,y in nullzip(self,vl2)]
        return self
    
    def __mul__(self, value):
        '''
Multiplies the vector by a scalar or by each component of another vector and
returns the resulting vector.

When used with a scalar, the length of the vector is multiplied with the scalar
while retaining the direction (unless the value is negative).
The simplified formula of scalar multiplication is:
vector * scalar == (x, y, z) * a = (x * a, y * a, z * a)

When used with another vector (any sequence with numerical items is OK),
the result is an uncommon vector resulted in multiplying the vectors by each
component separately.
The simplified formula for by-component vector multiplication is:
vector1 * vector2 == (x1, y1, z1) * (x2, y2, z2) = (x1 * x2, y1 * y2, z1 * z2)
        '''
        try:
            testzip = nullzip(self, value)
        except TypeError:
            return Vector((value*x for x in self))
        return Vector(((x*y) for x,y in testzip))
    __rmul__ = __mul__
    
    def __imul__(self, value):
        '''
Multiplies this vector by a scalar or by each component of another vector.

When used with a scalar, the length of the vector is multiplied with the scalar
while retaining the direction (unless the value is negative).
The simplified formula of scalar multiplication is:
vector * scalar == (x, y, z) * a = (x * a, y * a, z * a)

When used with another vector (any sequence with numerical items is OK),
the result is an uncommon vector resulted in multiplying the vectors by each
component separately.
The simplified formula for by-component vector multiplication is:
vector1 * vector2 == (x1, y1, z1) * (x2, y2, z2) = (x1 * x2, y1 * y2, z1 * z2)
        '''
        try:
            testzip = nullzip(self, value)
            self.vl = [(x*y) for x,y in testzip]
        except TypeError:
            for index, current_value in enumerate(self):
                self[index] = current_value * value
        return self
    
    def __div__(self, value):
        '''
Divides the vector by a scalar or by each component of another vector.

When used with a scalar, the length of the vector is divided with the scalar
while retaining the direction (unless the value is negative).
The simplified formula of scalar division is:
vector / scalar == (x, y, z) / a = (x / a, y / a, z / a)

When used with another vector (any sequence with numerical items is OK),
the result is an uncommon vector resulted in dividing the vectors by each
component separately.
The simplified formula for by-component vector division is:
vector1 / vector2 == (x1, y1, z1) / (x2, y2, z2) = (x1 / x2, y1 / y2, z1 / z2)
        '''
        try:
            testzip = nullzip(self, value)
        except TypeError:
            return Vector((x/value for x in self))
        return Vector(((x/y) for x,y in testzip))
    __truediv__ = __div__ # Ojii thought it would be a great idea to import division from future and break the maths logic
    
    def __idiv__(self, value):
        '''
Divides the vector by a scalar or by each component of another vector.

When used with a scalar, the length of the vector is divided with the scalar
while retaining the direction (unless the value is negative).
The simplified formula of scalar division is:
vector / scalar == (x, y, z) / a = (x / a, y / a, z / a)

When used with another vector (any sequence with numerical items is OK),
the result is an uncommon vector resulted in dividing the vectors by each
component separately.
The simplified formula for by-component vector division is:
vector1 / vector2 == (x1, y1, z1) / (x2, y2, z2) = (x1 / x2, y1 / y2, z1 / z2)
        '''
        try:
            testzip = nullzip(self, value)
        except TypeError:
            return Vector((x/value for x in self))
        return Vector(((x/y) for x,y in testzip))
    __itruediv__ = __idiv__
    
    def __getitem__(self, index):
        '''
Returns the value of the specified vector component.

Valid indexes are integer indexes < dimension of the vector and
special keywords "x", "y" and "z" which resolve to indexes 0, 1 and 2
respectively.
        '''
        if isinstance(index, slice):
            return Vector(self.vl[index])
        else:
            sindex = "xyz".find(str(index))
            if sindex >= 0:
                return self.vl[sindex]
            else:
                return self.vl[index]
            
    def __setitem__(self, index, value):
        '''
Replaces the value of the specified vector component.

Valid indexes are integer indexes < dimension of the vector and
special keywords "x", "y" and "z" which resolve to indexes 0, 1 and 2
respectively.
        '''
        if isinstance(index, slice):
            self.vl[index] = [float(x) for x in value]
        else:
            sindex = "xyz".find(str(index))
            if sindex >= 0:
                self.vl[sindex] = float(value)
            else:
                self.vl[index] = float(value)

    def __delitem__(self, index):
        '''
Deletes a component off the vector.

This reduces the dimension of the vector by 1 and reorders the adjacent
components.
        '''
        del self.vl[index]

    def __contains__(self, value):
        '''
Tests if the given value is one of the vector components.
        '''
        return value in self.vl

    def __eq__(self, vec2):
        '''
Test the equality of two vectors.

The vectors are considered to be equal when they have the same number of
components and all the respective components of both vectors are equal.
        '''
        return self.vl == vec2.vl
    
    def __ne__(self, vec2):
        '''
Test the inequality of two vectors.

The vectors are considered to be equal when they have the same number of
components and all the respective components of both vectors are equal.
The vectors are inequal otherwise.
        '''
        return self.vl != vec2.vl
    
    def __neg__(self):
        '''
Negates the vector.

The negation happens by negating all of the components separately.
The simplified formula of negating a vector:
-vector == -(x, y, z) = (-x, -y, -z)
        '''
        return Vector((-x for x in self.vl))

    def __iter__(self):
        '''
Returns an iterator to loop through every component of the vector.
        '''
        return iter(self.vl)

    def __reversed__(self):
        '''
Returns an iterator to loop through every component in reversed order.
        '''
        return reversed(self.vl)
    
    def copy(self):
        '''
Returns a new identical vector object.
        '''
        return Vector(self.vl)
    
    def ip(self, vec2):
        '''
Calculates the dot product (inner product with Cartesian space Spatial vectors).

Also known as Scalar product, the definition of inner product is:
a . b = |a|*|b|*cos(a,b)

The simplified formula for dot product is:
vector1.ip(vector2) == (x1, y1, z1) . (x2, y2, z2) = x1*x2 + y1*y2 + z1*z2
        '''
        return sum(a*b for a,b in zip(self, vec2))
    
    def cp(self, vec2):
        '''
Calculates the cross product of two three-dimensional vectors.

The cross product is defined as:
a x b = |a|*|b|*sin(a,b)*u
where u is a unit vector pointing to a direction perpendicular to both vectors.
In other words, the result is a vector that points to a direction perpendicular
to both of the original vectors, creating a normal for the plane defined by the
two vectors. The length of the resulting vector is equal to the area of a
parallelogram created using those two vectors.

The formula used here for cross product is:
vector1.cp(vector 2) == (x1, y1, z1) x (x2, y2, z2)
    = (y1*z2-z1*y2, z1*x2-x1*z2, x1*y2-y1*x2)
        '''
        if len(self) != 3 or len(vec2) != 3:
            raise TypeError('Cross product can only be calculated for vectors of three dimensions.')
        return Vector(
            self[1]*vec2[2] - self[2]*vec2[1],
            self[2]*vec2[0] - self[0]*vec2[2],
            self[0]*vec2[1] - self[1]*vec2[0]
            )
    
    def angle(self, vec2):
        ''' Calculates the angle between the two vectors in radians. '''
        try:
            return math.acos(self.ip(vec2)/(self.length()*Vector.length(vec2)))
        except ZeroDivisionError:
            raise ZeroDivisionError("Cannot calculate angle for zero vector")
    
    def angles(self, vec2):
        '''
Creates projections of the two vectors to the three planes (xy, yz, xz) and
calculates the angles between the projected vectors for each.

The returned value is a three-tuple containing the values in following order:
(yz, xz, xy). The returned angles are measured in radians.
        '''
        if len(self) != 3 or len(vec2) != 3:
            raise TypeError('Multiple angles can only be calculated for vectors of three dimensions.')
        ax = math.atan2(self[1],self[2])-math.atan2(vec2[1],vec2[2])
        ay = math.atan2(self[0],self[2])-math.atan2(vec2[0],vec2[2])
        az = math.atan2(self[0],self[1])-math.atan2(vec2[0],vec2[1])
        return ax,ay,az
    
    def length(self):
        '''
Returns the length/magnitude of the vector.

The simplified formula of calculating a vector length is:
length(vector) == |(x, y, z)| = sqrt(x**2 + y**2 + z**2)
        '''
        return sum(x*x for x in self)**.5
    
    def setlength(self, newlength):
        '''
Returns a new vector that has the same direction but the specified length.
        '''
        return self*(newlength/self.length())
    
    def normalize(self):
        '''
x.normalize()

    Returns a new vector that is the vector x with length 1.
        '''
        return self.setlength(1)
    
    # shortcuts for x, y and z coordinates
    x = property(
        lambda self: self.__getitem__(0),
        lambda self, value: self.__setitem__(0, value),
        None,
        'X coordinate value of the vector.')
    y = property(
        lambda self: self.__getitem__(1),
        lambda self, value: self.__setitem__(1, value),
        None,
        'Y coordinate value of the vector.')
    z = property(
        lambda self: self.__getitem__(2),
        lambda self, value: self.__setitem__(2, value),
        None,
        'Z coordinate value of the vector.')
    

# some helper functions
def distance(coord1, coord2):
    ''' Returns the distance between two points. '''
    return (Vector(coord1)-Vector(coord2)).length()

def viewangles(v1, v2, roll=0.0):
    '''
Returns tuple (pitch, yaw, roll) showing in which direction coord2 is from coord1.

The roll value cannot be determined by the vectors, so you will need to pass
it as an optional parameter (defaults to 0).
    '''
    height = v2[2]-v1[2]
    xl = v2[0]-v1[0]
    yl = v2[1]-v1[1]
    xylen = math.hypot(xl,yl)
    pitch = -math.degrees(math.atan2(height,xylen))
    yaw = math.degrees(math.atan2(yl,xl))
    if yaw < 0:
        yaw += 360
    return pitch, yaw, float(roll)

def viewvector(va):
    '''
Creates a vector of undefined length pointing to the direction specified as (pitch, yaw, roll) object.
    '''
    vangles = Vector(va)
    z = -math.sin(math.radians(vangles[0]))
    a = math.sqrt(1-z**2)
    x = a*math.cos(math.radians(vangles[1]))
    y = a*math.sin(math.radians(vangles[1]))
    return Vector((x,y,z))

def isbetweenRect(what, corner1, corner2):
    '''
Checks if a point is between a rectangular area specified by two opposite corners.
    '''
    min_iter = (min(comps) for comps in zip(corner1, corner2))
    max_iter = (max(comps) for comps in zip(corner1, corner2))
    for i in what:
        if i < next(min_iter) or i > next(max_iter):
            return False
    return True

def isbetweenVect(what, corner1, corner2):
    ''' Checks if a point is truly between a segment created by two points. '''
    v = Vector(what)
    c1 = Vector(corner1)
    c2 = Vector(corner2)
    if (v==c1 or v==c2):
        return True
    if c1==c2:
        return False
    return ((v[0]-c1[0])/(v[1]-c1[1])==(c2[0]-c1[0])/(c2[1]-c1[1]) and
            (v[0]-c1[0])/(v[2]-c1[2])==(c2[0]-c1[0])/(c2[2]-c1[2]) and
            (v[2]-c1[2])/(v[1]-c1[1])==(c2[2]-c1[2])/(c2[1]-c1[1]))

def distance_from_line(point, line_coord1, line_coord2):
    ''' Returns the distance of point from a line specified by two coordinates. '''
    c = Vector(point)
    a = Vector(line_coord1)
    b = Vector(line_coord2)
    if a==b:
        raise ValueError(f'Identical points ({a.getstr(", ")}) cannot form unique line.')
    p = c-a
    s = b-a
    t = s * (ip(p,s)/ip(s,s))
    d = p-t
    return d.length()

def distance_from_segment(point, start, end, allow_outside=True):
    '''
Returns the distance of point from a segment between start and end points.

If allow_outside is False, then ValueError is raised if the point is outside the segment.
    '''
    c = Vector(point)
    a = Vector(start)
    b = Vector(end)
    if a==b:
        raise ValueError(f'Identical points ({a.getstr(", ")}) cannot form unique line.')
    p = c-a
    s = b-a
    sp = ip(p,s)
    if (sp <= 0):
        # the point is behind start
        if not allow_outside:
            raise ValueError(f'Point ({c.getstr(", ")}) is behind the starting point of ({a.getstr(", ")}) - ({b.getstr(", ")})')
        return p.length()
    lp = ip(s,s)
    if (lp <= sp):
        # the point is behind end
        if not allow_outside:
            raise ValueError(f'Point ({c.getstr(", ")}) is behind the ending point of ({a.getstr(", ")}) - ({b.getstr(", ")})')
        return distance(c,b)
    # the point is next to the line
    d = p - (s * (sp/lp))
    return d.length()

def distance_from_ray(point, start, line_coord, allow_outside=True):
    '''
Returns the distance of "point" from a ray starting from "start" point and then
continuing indefinitely passing "line_coord".

If allow_outside is False, then ValueError is raised if the point is behind starting point.
    '''
    c = Vector(point)
    a = Vector(start)
    b = Vector(line_coord)
    if a==b:
        raise ValueError(f'Identical points ({a.getstr(", ")}) cannot form unique line.')
    p = c-a
    s = b-a
    sp = ip(p,s)
    if (sp <= 0):
        # the point is behind start
        if not allow_outside:
            raise ValueError('Point ({c.getstr(", ")}) is behind the starting point of the ray from ({a.getstr(", ")}) by ({b.getstr(", ")})')
        return p.length()
    lp = ip(s,s)
    d = p - (s * (sp/lp))
    return d.length()




#backwards compatibility:
vector = Vector
