import es

def load():
    vectors()
    cmdtest()
    

def vectors():
    y = es.createvectorstring(3.5,4.5,6.8)
    if y != "3.500000,4.500000,6.800000":
        print "failed",y
    else:
        print "success1",y
    z = es.splitvectorstring(y)
    if z[0] != 3.5 or z[1] != 4.5 or round(z[2],1) != 6.8:
        print "failed2",z
    else:
        print "success2",z

def cmdtest():
    cmdtest_register()
    es.server.cmd("pycommand2")
    
def cmdtest_register():
    es.regcmd("pycommand2", "pyunittest/sub/cmdtest_run", "Stuff")
    
def cmdtest_run():
    es.set("cmdtest_pass2", 1)
    print "cmdtest()"
