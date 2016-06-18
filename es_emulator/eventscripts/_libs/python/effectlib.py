import es
import vecmath
from vecmath import vector


"""
effectlib, holds functions for some special effects
"""

def drawLine(coord1, coord2,
            model="materials/sprites/laser.vmt",
            halo="materials/sprites/halo01.vmt",
            seconds=0,
            width=10,
            endwidth=10,
            red=255,
            green=255,
            blue=255,
            brightness=255,
            speed=10,
            fadelength=0,
            noise=0,
            framestart=0,
            framerate=0):
    """
Draw a line between two coordinates
    """
    try:
        c1 = vector(coord1)
        c2 = vector(coord2)
    except TypeError:
        raise TypeError("Invalid parameter type for coordinates")
    # Draw it!
    mi = es.precachemodel(model)
    hi = es.precachemodel(halo)
    es.effect('beam', str(c1), str(c2), mi, hi,
              framestart, framerate,
              seconds, width, endwidth, fadelength, noise,
              red, green, blue, brightness, speed)


def drawBox(coord1, coord2,
            model="materials/sprites/laser.vmt",
            halo="materials/sprites/halo01.vmt",
            seconds=0,
            width=10,
            endwidth=10,
            red=255,
            green=255,
            blue=255,
            brightness=255,
            speed=10,
            fadelength=0,
            noise=0,
            framestart=0,
            framerate=0):
    """
Draw a rectangular box by using two coordinates
    """
    try:
        c1 = vector(coord1)
        c2 = vector(coord2)
    except TypeError:
        raise TypeError("Invalid parameter type for coordinates")
    # Create the additional corners for the box
    tc1 = vector(c1)
    tc2 = vector(c1)
    tc3 = vector(c1)
    tc4 = vector(c2)
    tc5 = vector(c2)
    tc6 = vector(c2)
    tc1[0] = c2[0]
    tc2[1] = c2[1]
    tc3[2] = c2[2]
    tc4[0] = c1[0]
    tc5[1] = c1[1]
    tc6[2] = c1[2]
    # Draw all the edges
    mi = es.precachemodel(model)
    hi = es.precachemodel(halo)
    es.effect('beam', str(c1), str(tc1), mi, hi,
              framestart, framerate,
              seconds, width, endwidth, fadelength, noise,
              red, green, blue, brightness, speed)
    es.effect('beam', str(c1), str(tc2), mi, hi,
              framestart, framerate,
              seconds, width, endwidth, fadelength, noise,
              red, green, blue, brightness, speed)
    es.effect('beam', str(c1), str(tc3), mi, hi,
              framestart, framerate,
              seconds, width, endwidth, fadelength, noise,
              red, green, blue, brightness, speed)
    es.effect('beam', str(tc6), str(tc1), mi, hi,
              framestart, framerate,
              seconds, width, endwidth, fadelength, noise,
              red, green, blue, brightness, speed)
    es.effect('beam', str(tc6), str(tc2), mi, hi,
              framestart, framerate,
              seconds, width, endwidth, fadelength, noise,
              red, green, blue, brightness, speed)
    es.effect('beam', str(tc6), str(c2), mi, hi,
              framestart, framerate,
              seconds, width, endwidth, fadelength, noise,
              red, green, blue, brightness, speed)
    es.effect('beam', str(tc4), str(c2), mi, hi,
              framestart, framerate,
              seconds, width, endwidth, fadelength, noise,
              red, green, blue, brightness, speed)
    es.effect('beam', str(tc5), str(c2), mi, hi,
              framestart, framerate,
              seconds, width, endwidth, fadelength, noise,
              red, green, blue, brightness, speed)
    es.effect('beam', str(tc5), str(tc1), mi, hi,
              framestart, framerate,
              seconds, width, endwidth, fadelength, noise,
              red, green, blue, brightness, speed)
    es.effect('beam', str(tc5), str(tc3), mi, hi,
              framestart, framerate,
              seconds, width, endwidth, fadelength, noise,
              red, green, blue, brightness, speed)
    es.effect('beam', str(tc4), str(tc3), mi, hi,
              framestart, framerate,
              seconds, width, endwidth, fadelength, noise,
              red, green, blue, brightness, speed)
    es.effect('beam', str(tc4), str(tc2), mi, hi,
              framestart, framerate,
              seconds, width, endwidth, fadelength, noise,
              red, green, blue, brightness, speed)


def drawCircle(origin, radius, steps=12,
            axle1=(1,0,0),
            axle2=(0,1,0),
            normal=None,
            model="materials/sprites/laser.vmt",
            halo="materials/sprites/halo01.vmt",
            seconds=0,
            width=10,
            endwidth=10,
            red=255,
            green=255,
            blue=255,
            brightness=255,
            speed=10,
            fadelength=0,
            noise=0,
            framestart=0,
            framerate=0):
    """
Draw a circle on a plane defined by origin and two points (axles)
    """
    try:
        o = vector(origin)
        a1 = vector(axle1)
        if not normal:
            a2 = vector(axle2)
            normal = a1.cp(a2)
    except TypeError:
        raise TypeError("Invalid parameter type for coordinates")
    
    # normalize steps to be modular by 4, rounding up
    steps = int(float(steps)/4.0+.9)*4
    # calculate steps per line
    edgesteps = steps/4

    # generate the corner vectors
    k = []
    k.append(a1.setlength(radius))
    k.append(normal.cp(a1).setlength(radius))
    k.append(-k[0])
    k.append(-k[1])
    k.append(k[0])

    # distance between steps
    steplength = vecmath.distance(k[0],k[1])/edgesteps
    
    # Draw all the edges
    mi = es.precachemodel(model)
    hi = es.precachemodel(halo)
    for edge in range(4):
        c1 = o+k[edge]
        minus = k[edge+1]-k[edge]
        for s in range(edgesteps):
            c2 = o+(k[edge]+minus.setlength(steplength*(s+1))).setlength(radius)
            es.effect('beam', str(c1), str(c2), mi, hi,
              framestart, framerate,
              seconds, width, endwidth, fadelength, noise,
              red, green, blue, brightness, speed)
            c1 = c2
