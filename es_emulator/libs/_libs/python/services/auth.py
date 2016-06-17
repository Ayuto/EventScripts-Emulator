import services

class AuthorizationService(services.Service):
  ROOT          = 0
  ADMIN         = 1
  POWERUSER     = 2
  IDENTIFIED    = 4
  UNRESTRICTED  = 128

  def registerCapability(self, auth_capability, auth_recommendedlevel):
    '''
    When a script loads and it needs a new capability, it calls this
    function to notify the authorization service that it may need to ask
    for this capability.
    e.g. in your script load:
    auth.registerCapability("some_capability", auth.ADMIN)
    '''
    raise NotImplementedError

  def isUseridAuthorized(self, auth_userid, auth_capability):
    '''
    This is likely the most commonly called method here. A script can call
    this and it will return a 1 or 0 depending on whether the user is
    authorized for the capability.
    Example:
    auth.isUseridAuthorized(int(event_var['userid']),"some_capability")
    '''
    raise NotImplementedError

  def getOfflineIdentifier(self, auth_userid):
    '''
    This function returns some semi-unique identifier for a current userid
    that can be used to check authorization while a user is offline.
    This may very often be a steamid/uniqueid or somesuch identifier.
    Example:
    auth.getOfflineIdentifier(event_var['userid'])
    '''
    raise NotImplementedError

  def isIdAuthorized(self, auth_identifier, auth_capability):
    '''
    This function is like isUseridAuthorized, but requires an offline ID
    from the getOfflineIdentifier function. Typically isUseridAuthorized
    is just a wrapper to getOfflineIdentifier followed by isIdAuthorized.
    :auth isIdAuthorized <aauth_outputvarname> <auth_identifier>
    es :auth isIdAuthorized myvar server_var(myidentifier)
    '''
    raise NotImplementedError