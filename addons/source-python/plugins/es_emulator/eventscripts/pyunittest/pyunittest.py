import es
import unittest
from es import server_var

info = es.AddonInfo()
info.name     = "Python Unit Test Script"
info.version  = "1.1"
info.url      = "http://mattie.info/cs"
info.basename = "pyunittest"
info.author   = "Mattie" 

pytests = unittest.TestSuite()

def addTestCase(testcase):
    print("[Tests] Adding testcase: ", testcase.__name__)
    ldr = unittest.TestLoader()
    pytests.addTests(ldr.loadTestsFromTestCase(testcase)._tests)

class PyTestOutput():
    def __init__(self, level=0):
      self.level = level
    def write(self, data):
      self.writeln(data)
    def writeln(self, data=''):
      es.dbgmsg(self.level, '[Tests]: %s' % data)

def load():
    runner = unittest.TextTestRunner()
    runner.stream = PyTestOutput()
    runner.run(pytests)

class SvarTests(unittest.TestCase):
  def setUp(self):
    self.oldgravity = int(es.ServerVar("sv_gravity"))
    es.ServerVar("sv_gravity").set(800)
  def tearDown(self):
    es.ServerVar("sv_gravity").set(self.oldgravity) 
  def testSvar(self):
      s = es.ServerVar("sv_gravity")
      text = str(s)
      self.failUnless(text == "800")
      val = int(s)
      self.failUnless(val == 800)
      fl = float(s)
      self.failUnless(fl == 800.0)
      bl = bool(s)
      self.failUnless(fl)
      self.failUnless(s.getName() == "sv_gravity")
  def testCoerce(self):
      s = es.ServerVar("sv_gravity")
      s.set(795)
      self.failUnless(s == 795)
      self.failUnless(s == "795")
      self.failUnless(s == True)
addTestCase(SvarTests)

class WhileTests(unittest.TestCase):
  def testWhile(self):
    i = 5000
    es.set("myvar", 5000)
    while i:
        i-=1
        es.server.cmd("es_xmath myvar - 1")
    self.failUnless(int(server_var['myvar'])==0)
addTestCase(WhileTests)

    
class VectorTests(unittest.TestCase):
  def testSvar(self):
      y = es.createvectorstring(3.5,4.5,6.8)
      self.failUnless(y == "3.500000,4.500000,6.800000")
      z = es.splitvectorstring(y)
      self.failIf(z[0] != 3.5 or z[1] != 4.5 or round(z[2],1) != 6.8)
addTestCase(VectorTests)

# begin CmdTests section
class CmdTests(unittest.TestCase):
  def setUp(self):
    # lets suppress some noise
    debug = es.ServerVar("eventscripts_debug")
    olddebug = int(debug)
    if int(debug) == 0:
      debug.set(-1)
    es.regcmd("pycommand", "pyunittest/cmdtest_run", "Stuff")
    debug.set(olddebug)
    es.regsaycmd("pycommand","pyunittest/cmdtest_run", "Stuff")
    es.regclientcmd("pycommand","pyunittest/cmdtest_run", "Stuff")
  def tearDown(self):
    es.unregsaycmd("pycommand")
    es.unregclientcmd("pycommand")
  def testCmd(self):
      es.server.cmd("pycommand passed")
      self.failUnless(server_var['cmdtest_pass'] == "passed")
      self.failUnless(server_var['cmdtest_pass2'] == "passed")
  def testQueryCmd(self):
      self.failUnless(es.queryregcmd("pycommand_doesntexist")==  "")
      self.failUnless(es.queryregsaycmd("pycommand_doesntexist")==  "")
      self.failUnless(es.queryregclientcmd("pycommand_doesntexist")==  "")
      self.failUnless(es.queryregcmd("pycommand")==  "pyunittest/cmdtest_run")
      self.failUnless(es.queryregsaycmd("pycommand")==  "pyunittest/cmdtest_run")
      self.failUnless(es.queryregclientcmd("pycommand")==  "pyunittest/cmdtest_run")
      self.failUnless(es.getHelpText("pycommand") == "Stuff")
addTestCase(CmdTests)
    
def cmdtest_run():
    es.set("cmdtest_pass", es.getargv(1))
    #print "cmdtest(), args: %s, argc: %d" % (es.getargs(), es.getargc())
    if es.getargc() != 2:
      print("cmdtest0_failed,", es.getargc())
    es.doblock("pyunittest/cmdtest_block")

def cmdtest_block():
    es.set("cmdtest_pass2", es.getargv(1))
# end CmdTests section

class KeyTests(unittest.TestCase):
  def setUp(self):
      pass
  def tearDown(self):
      pass
  def keytest2(self, x):
      self.failIf(x <= 0)
      name = es.keypgetname(x)
      self.failIf(name != "justice")
      es.keypsetname(x, "justice2")
      name = es.keypgetname(x)
      self.failIf(name != "justice2")
      y = es.keypfindsubkey(x, "subkey", False)
      self.failUnless(y is None)
      y = es.keypfindsubkey(x, "subkey", True)
      subname = es.keypgetname(y)
      self.failUnless(subname == "subkey")
      r = es.keypfindsubkey(x, "subkey", True)
      self.failUnless(r==y)
      q = es.keypfindsubkey(x, "subkey2", True)
      subname = es.keypgetname(q)
      self.failIf(subname != "subkey2")
      w = es.keypfindsubkey(x, "subkey3", True)
      e = es.keypfindsubkey(x, "subkey3", True)
      p = es.keypgetfirstsubkey(x)
      n = 0
      while p:
        n+=1
        p = es.keypgetnextkey(p)
      self.failUnless(n==3)
      self.failUnless(w==e)
      es.keypdetachsubkey(x, w)
      e = es.keypfindsubkey(x, "subkey3", False)
      self.failUnless(e is None)
      es.keypdelete(w)
      p = es.keypgetfirstsubkey(x)
      n = 0
      while p:
        n+=1
        p = es.keypgetnextkey(p)
      self.failUnless(n==2)
      self.failUnless(es.keypisempty(r))
      # setstring    
      es.keypsetstring(r, "hello", "1.3")
      self.failIf(es.keypisempty(r))
      outcome = es.keypgetstring(y, "hello")
      self.failUnless(outcome=="1.3")
      outcome = es.keypgetint(y, "hello")
      self.failUnless(outcome == 1)
      outcome = es.keypgetfloat(y, "hello")
      self.failUnless(round(outcome,1) == 1.3)
      # setint
      es.keypsetint(y, "hello", 99)
      outcome = es.keypgetint(y, "hello")
      self.failUnless(outcome==99)
      # setfloat
      es.keypsetint(y, "hello", 99)
      outcome = es.keypgetint(y, "hello")
      self.failUnless(outcome==99)
      # save to file
      es.keypsavetofile(x, server_var['eventscripts_addondir'] + "/pyunittest/myfile.vdf")

  def keytest3(self,x):
      es.keyploadfromfile(x, server_var['eventscripts_addondir'] + "/pyunittest/myfile.vdf")
      y = es.keypfindsubkey(x, "subkey", False)
      outcome = es.keypgetint(y, "hello")
      self.failUnless(outcome==99)
      z = es.keypfindsubkey(y, "test", True)
      name = es.keypgetname(z)
      self.failUnless(name =="test")
      pp = es.keypcreate()
      es.keyploadfromfile(pp, server_var['eventscripts_addondir'] + "/pyunittest/myfile.vdf")
      es.keyprecursivekeycopy(z, pp)
      name = es.keypgetname(z)
      self.failUnless(name == "justice2")

  def testKeygroup(self):
      es.keygroupcreate("justice")
      x = es.keygroupgetpointer("justice")
      self.keytest2(x)
      es.keygroupdelete("justice2")
      es.keygroupcreate("justice2")
      x = es.keygroupgetpointer("justice2")
      self.keytest3(x)
      import keyvalues
      y = keyvalues.getKeyGroup("justice2")
      es.keygroupdelete("justice2")

  def testNewkey(self):
      x = es.keypcreate()
      es.keypsetname(x, "justice")
      self.keytest2(x)
      es.keypdelete(x)
      x = es.keypcreate()
      es.keypsetname(x, "justice2")
      self.keytest3(x)
      es.keypdelete(x)
      return
addTestCase(KeyTests)

class CreateScriptListTest(unittest.TestCase):
  def testCreatescriptlist(self):
      j = es.createscriptlist()
      self.failUnless(j and len(j))
      j = es.createscriptlist("xxxxxxxxlarry")
      self.failIf(j or len(j))
      j = es.createscriptlist('corelib')
      self.failUnless(len(j)==1)
addTestCase(CreateScriptListTest)

class MaxPlayerTests(unittest.TestCase):
  def testGetmaxplayers(self):
      j = es.getmaxplayercount()
      self.failUnless(j)
      # in CS:S we know the max players is cs_team_manager index -1 
      if es.getgame() == "Counter-Strike: Source":
        q = es.getentityindex('cs_team_manager') - 1
        if q:
          self.failUnless(q==j)
addTestCase(MaxPlayerTests)
