import msglib
import keyvalues
import es


def load():
  print("msgtests loaded, waiting for player to say !go")
  
  
def player_say(event_var):
  # probably the best way
  if event_var['text'] == "!menu":
    dlg = msglib.VguiDialog(title="menu1", msg="themessage", mode=msglib.VguiMode.MENU)
    dlg["msg"] = "This is a long message.\nYes it is! Never forget me!\n\n\nNo!\n"
    dlg.addOption(msg="Hello", command="echo Hello")
    dlg.addOption(msg="Hello1", command="echo Hello1")
    dlg.addOption(msg="Hello2", command="echo Hello2")
    dlg.addOption(msg="Hello3", command="echo Hello3")
    dlg.addOption(msg="Hello4", command="echo Hello4")
    dlg = msglib.VguiDialog(title="My Title", msg="My Message", mode=msglib.VguiMode.TEXT)
    dlg.send(event_var['userid'])

  # keyvalue way if you want
  if event_var['text'] == "!go":
    kv = keyvalues.KeyValues(name="message")
    kv["msg"] = "THIS IS THE MESSAGE"
    kv["title"] = "TITLE!"
    kv["level"] = 5
    kv["color"] = "255 255 0 255"
    kv["time"] = 20
    for x in kv:
      print(x.getName(), kv[x.getName()])
    msglib.sendVguiDialog(event_var['userid'], msglib.VguiType.TEXT, kv)

    
