import es
# tricky import trick
sauth = __import__("services.auth")
services = __import__("services")

import keyvalues

#//services getlist mykeygroup
#//services getregistered myvar auth
#//services type auth requires AuthorizationService 1
#//services list
#  interface instance basic_auth implements AuthorizationService version 1
#  interface instance basic_auth invokes examples/auth/basic_auth/command_block

legacyinterfaces = {}


#py2e
class LegacyAuthorizationService(services.auth.AuthorizationService):
  def setCommandName(self, name):
    self.cmdname = name
    self.name = name
    self.__var = es.ServerVar("__LegacyAuthorizationService-returnvar", 0, "LegacyAuthorizationService return variable. Internal use.")
  def registerCapability(self, auth_capability, auth_recommendedlevel):
    es.server.cmd("%s registerCapability %s %d" % (self.cmdname, auth_capability, auth_recommendedlevel))
  def isUseridAuthorized(self, auth_userid, auth_capability):
    self.__var.set(0)
    es.server.cmd("%s isUseridAuthorized %s %d %s" %(self.cmdname, self.__var.getName(), auth_userid, auth_capability))
    return bool(int(self.__var))
  def getOfflineIdentifier(self, auth_userid):
    self.__var.set(0)
    es.server.cmd("%s getOfflineIdentifier %s %d" %(self.cmdname, self.__var.getName(), auth_userid))
    return str(self.__var)
  def isIdAuthorized(self, auth_identifier, auth_capability):
    self.__var.set(0)
    es.server.cmd("%s isIdAuthorized %s %s %s" %(self.cmdname, self.__var.getName(), auth_identifier, auth_capability))
    return bool(int(self.__var))

def load():
  es.regcmd("services", "corelib/services/services_cmd", "Defines a one-of-a-kind service that requires a specific interface")
  es.regcmd(":", "corelib/services/services_proxy", "Invoke a service command")

def services_cmd():
  # handles all of the service related functions
  cmd = es.getargv(1)
  cmd = cmd.lower()
  if   cmd == "register":
    # create a fake service
    # //services register auth myauth
    # // services.register("auth", myauth)
    servicename = es.getargv(2)
    cmdname = es.getargv(3)
    leg = LegacyAuthorizationService()
    leg.setCommandName(cmdname)
    services.register(servicename, leg)
  elif cmd == "unregister":
    servicename = es.getargv(2)
    services.unregister(servicename)
    # // services unregister auth
    pass
  elif cmd == "isregistered":
    # //services isregistered myvar auth
    returnvar = es.ServerVar(es.getargv(2))
    servicename = es.getargv(3)
    returnvar.set(int(services.isRegistered(servicename)))
  elif cmd == "getlist":
    pass
  elif cmd == "getregistered":
    pass
  elif cmd == "type":
    pass
  elif cmd == "list":
    pass
  else:
    es.dbgmsg(0, "services: Invalid option.")

returnvarlist = {
  'registerCapability':0,
  'isUseridAuthorized':3,
  'getOfflineIdentifier':3,
  'isIdAuthorized':3
}

# DEPRECATED -- ONLY SUPPORTED FOR AUTHORIZATION SERVICE  
#// :auth isauthorized <output-var> <user-identifier> <action-name> <action-level>
def services_proxy():
  service = es.getargv(1)
  myserv = services.use(service)
  if not isinstance(myserv, LegacyAuthorizationService):
    # e2py
    function = es.getargv(2)
  
    # HACK: For auth services
    responsevarn = 0
    responsevar = None
    if service=="auth":
      # fix the case of the function
      for caser in returnvarlist.keys():
        if caser.lower() == function.lower():
          function = caser
      responsevarn = returnvarlist[function] if returnvarlist.has_key(function) else 0
      if responsevarn:
        responsevar = es.ServerVar(es.getargv(responsevarn))
    
    arglist = [myserv]
    for j in range(3,es.getargc()):
      if not j == responsevarn:
        arglist.append(es.getargv(j))
    func = myserv.__class__.__dict__[function]
    d = func(*arglist)
    if d is not None and responsevar is not None:
      responsevar.set(d)
  else:
    # e2e
    cmd = myserv.cmdname
    args = es.getargs()[len(service)+1:]
    newcmd = "%s %s" % (cmd, args)
    es.server.cmd(newcmd)
    

# //services register auth myauth
# // services.register("auth", myauth)
# def register(name, service):
#   if GlobalServices.has_key(name):
#     raise ExistingServiceException, "%s already exists as a registered service." % name
#   if not isinstance(service, Service): 
#     raise InvalidServiceException, "%s is not a Service instance" % name
#   GlobalServices[name] = service
# 
# // services unregister auth
# // services.unregister("auth")
# def unregister(name):
#   if not GlobalServices.has_key(name):
#     raise KeyError, "%s is not a registered service." % name
#   del GlobalServices[name]
# 
# 
# // :auth isauthorized <output-var> <user-identifier> <action-name> <action-level>
# def use(name):
#   return GlobalServices[name]
# 
# //services isregistered myvar auth
# def isRegistered(name):
#   return GlobalServices.has_key(name)
# 
# def getList():
#   return GlobalServices.keys()
