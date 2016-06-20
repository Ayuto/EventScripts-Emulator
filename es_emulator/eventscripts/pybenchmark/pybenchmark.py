import psyco
psyco.full()
import time
import math
import keyvalues

math_int_loops = 2000
math_float_loops = 2000
string_op_loops = 2000
string_fmt_loops = 2000
string_ml_loops = 2000
string_rplc_loops = 2000
g_Prof = {}

def load():
    # PrintToServer("dictionary time: %f seconds", g_dict_time);
    string_bench()
    math_bench()
    dict_bench()
    keyalues_bench()

def StartProfiling(storage):
    storage['start'] = time.clock()
    # take snapshot

def StopProfiling(storage):
    # take snapshot
    storage['stop'] = time.clock()
    
def GetProfilerTime(storage):
    return storage['stop'] - storage['start']
  
def math_bench():
    StartProfiling(g_Prof)
    iter1 = math_int_loops
    a = 0
    b = 0
    c = 0
    while iter1:
        iter1 = iter1 - 1
        a = iter1 * 7
        b = 5 + iter1
        c = 6 / (iter1 + 3)
        a = 6 * (iter1)
        b = a * 185
        a = b / 25
        c = b - a + 3
        b = b*b
        a = (a + c) / (b - c)
        b = 6
        c = 1
        b = a * 128 - c
        c = b * (a + 16) * b
        if not a:
            a = 5;
        a = c + (28/a) - c;
    StopProfiling(g_Prof);
    print("int benchmark: %f seconds" % GetProfilerTime(g_Prof))
    StartProfiling(g_Prof)	
    fa = 0.0
    fb = 0.0
    fc = 0.0
    int1 = 0
    iter1 = math_float_loops;
    while iter1:
        iter1 = iter1 - 1
        fa = iter1 * 0.7
        fb = 5.1 + iter1
        fc = 6.1 / (float(iter1) + 2.5)
        fa = 6.1 * (iter1)
        fb = fa * 185.26
        fa = fb / 25.56
        fc = fb - a + float(3)
        fb = fb*fb
        fa = (fa + fc) / (fb - fc)
        fb = 6.2
        fc = float(1)
        int1 = round(fa)
        fb = fa * float(128) - int1
        fc = fb * (a + 16.85) * float((fb))
        if fa == 0.0:
            fa = 5.0
        fa = fc + (float(28)/fa) - math.floor(fc);
    StopProfiling(g_Prof)
    print("float benchmark : %f seconds" % GetProfilerTime(g_Prof))

key1 = "LVWANBAGVXSXUGB"
key2 = "IDYCVNWEOWNND"
key3 = "UZWTRNHY"
key4 = "EPRHAFCIUOIG"
key5 = "RMZCVWIEY"
key6 = "ZHPU"

def string_bench():
    i = string_fmt_loops;
    buffer = ''
    
    StartProfiling(g_Prof);
    while i:
        i = i -1
        buffer = "%d" % i
        buffer = "%d %s %d %f %d %-3.4s %s" % (i, "gaben", 30, 10.0, 20, "hello", "What a gaben")
        buffer = "Well, that's just %-17.18s!" % ("what.  this isn't a valid string! wait it is")
        buffer = buffer + "There are %d in this %d" % (i, len(buffer))
        buffer = buffer +  "There are %d in this %d" % (i, len(buffer))
    StopProfiling(g_Prof);
    print("format() benchmark: %f seconds" % GetProfilerTime(g_Prof))

    fmtbuf = "4567899"
    StartProfiling(g_Prof);
    i = string_op_loops;
    while i:
        i = i -1
        int(fmtbuf)
    StopProfiling(g_Prof);
    print("str benchmark: %f seconds" % GetProfilerTime(g_Prof))


    StartProfiling(g_Prof);
    i = string_rplc_loops
    while i:
        i = i -1
        fmtbuf = "This is a test string for you."
        fmtbuf = fmtbuf.replace(" ", "ASDF")
        fmtbuf = fmtbuf.replace("SDF", "")
        fmtbuf = fmtbuf.replace("string", "gnirts")
    StopProfiling(g_Prof);
    print("replace benchmark: %f seconds" % GetProfilerTime(g_Prof))

import random
import types

def create(typ, num):
    j = typ()
    for i in range(num):
      if typ == keyvalues.KeyValues:
        j[str(i)] = typ(name=str(i))
      else:
        j[str(i)] = typ()
      j[str(i)]["top"] = random.randint(1, num+1)
    return j

def dictlike_bench(typ, num):
    src = create(typ, num)
    StartProfiling(g_Prof);
    top = -1000
    itertarget = None
    if typ == keyvalues.KeyValues:
      itertarget = src
    else:
      itertarget = list(src.values())
    for item in itertarget:
      val = item["top"]
      if val > top:
        top = val
    StopProfiling(g_Prof);
    print("%s benchmark: %f seconds" % (typ, GetProfilerTime(g_Prof)))

def dict_bench():
  dictlike_bench(dict, 10000)
  
def keyalues_bench():
  dictlike_bench(keyvalues.KeyValues, 10000)
  
  
