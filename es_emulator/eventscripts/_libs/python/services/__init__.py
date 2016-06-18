class Service(object):
  pass
# // :auth isauthorized <output-var> <user-identifier> <action-name> <action-level>
# //services getlist mykeygroup
# //services getregistered myvar auth
# //services type auth requires AuthorizationService 1
# //services register auth myauth
# //services unregister auth
# //services list
# //services isregistered myvar auth

GlobalServices = {}

class InvalidServiceException(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class ExistingServiceException(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class Service(object):
  def __init__(self):
    self.interfacename = None
    self.version = None
    self.name = None
  def checkInterfaces(self):
    # TODO
    for name in self.required:
      if name not in self.__dict__:
        raise InvalidServiceException("%s method is not implemented but is required" % name)

# //services register auth myauth
# // services.register("auth", myauth)
def register(name, service):
  if name in GlobalServices:
    raise ExistingServiceException("%s already exists as a registered service." % name)
  if not isinstance(service, Service):
    raise InvalidServiceException("%s is not a Service instance" % name)
  GlobalServices[name] = service

# // services register auth myauth
# // services.unregister("auth")
def unregister(name):
  if name not in GlobalServices:
    raise KeyError("%s is not a registered service." % name)
  del GlobalServices[name]

def use(name):
  return GlobalServices[name]

# //services isregistered myvar auth
def isRegistered(name):
  return name in GlobalServices

def getList():
  return list(GlobalServices.keys())

def getRegisteredName(name):
  if name in GlobalServices:
    sv = GlobalServices[name]
    if "name" in sv.__dict__:
      return sv.name
    else:
      return str(sv)
  return None
