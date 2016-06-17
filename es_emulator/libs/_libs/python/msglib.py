
import keyvalues
import playerlib
import es


class VguiMode:
  MSG        = 0
  MENU       = 1
  TEXT       = 2
  ENTRY      = 3
  ASKCONNECT = 4

def sendVguiDialogKeygroup(userid, msgtype, keyname):
  key = keyvalues.getKeyGroup(keyname)
  if not id:
    raise KeyError(keyname)
  es.sendkeypmsg(int(userid), int(msgtype), key['message']._id_)

def sendVguiDialog(userid, msgtype, key):
  es.sendkeypmsg(int(userid), int(msgtype), key._id_)

class VguiDialog(object):
  def __init__(self, title="Dialog", msg="Dialog", level=5, color="255 255 255 255", time=10, mode=VguiMode.MSG):
    self.kv = keyvalues.KeyValues(name=title)
    self.kv['title'] = title
    self.kv['msg'] = msg
    self.kv['level'] = level
    self.kv['color'] = color
    self.kv['time'] = time
    self.mode = mode
    self.nextoption = 1
  def send(self, userid):
    sendVguiDialog(userid, self.mode, self.kv)
  def __setitem__(self, name, value):
    self.kv[name] = value
  def addOption(self, msg="Option", command="echo 1"):
    names = str(self.nextoption)
    self.kv[names] = keyvalues.KeyValues(name=names)
    self.kv[names]["msg"] = msg
    self.kv[names]["command"] = command
    self.nextoption = self.nextoption + 1
