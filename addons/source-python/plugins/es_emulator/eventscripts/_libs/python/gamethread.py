'''
This module lets you execute things later within the primary gamethread.
It provides access to queues and delayed command management such that you
can interact safely with the server from external threads.
'''

import es
import time
import queue
import threading
import bisect

q = queue.Queue()
register_lock = threading.Lock()
tickreg = False;

class TimeSortedQueue(object):
  class TimeNode(object):
    def __init__(self, gotime, cmd, name):
      self.name = name
      self.gotime = float(gotime)
      self.cmd = cmd
    def __lt__(self, b):
      return self.gotime < b.gotime
    def __eq__(self, b):
      return self.gotime == b.gotime
    def __gt__(self, b):
      return self.gotime > b.gotime
  def __init__(self):
    self.nodes = []
    self.lock = threading.Lock()
  def addNode(self, node):
    with self.lock:
      bisect.insort(self.nodes, node)
  def add(self, gotime, cmd, args=(), kw=None, name=None):
    if not isinstance(args, tuple):
      args = (args,)
    self.addNode(self.TimeNode(gotime,(cmd, args, kw or {}),name))
  def getFirst(self):
    with self.lock:
      if self.nodes:
        return self.nodes[0]
      else:
        return None
  def getList(self):
    with self.lock:
      return self.nodes
  def removeByName(self, name):
    if not name: return   # can't kill items with no name
    with self.lock:
      self.nodes = [i for i in self.nodes if i.name != name]
  def remove(self, item):
    with self.lock:
      if item in self.nodes:
        self.nodes.remove(item)
  def empty(self):
    with self.lock:
      return not bool(self.nodes)
  def printQueue(self):
    with self.lock:
      for i in self.nodes:
        es.dbgmsg(0, "[%8s] in %s seconds from now,\n  %s\n" % (i.name, i.gotime - time.time(), i.cmd))

timeq = TimeSortedQueue()


##################################
# begin public external interfaces
# begin public external interfaces

def delayed(seconds, cmd, args=(), kw=None):
    '''
    Executes a Python function at a later time. Requires a map to be started
    on the server (and ticks to be firing). Args can be passed in as a tuple,
    or as keyword argments. This is like a Python-based es_delayed.
    '''
    registerTicker()
    timeq.add(time.time()+seconds, cmd, args, kw)

def delayedname(seconds, name, cmd, args=(), kw=None):
    '''
    Executes a Python function at a later time. Requires a map to be started
    on the server (and ticks to be firing). Args can be passed in as a tuple,
    or as keyword argments. This is like a Python-based es_delayed.

    Use delayedname if you want to provide an identifier that can be used with
    cancelDelayed(identifier) to stop the execution before it happens.
    '''
    registerTicker()
    timeq.add(time.time()+seconds, cmd, args, kw, name)

def cancelDelayed(name):
    '''
    Cancel a command by name that was scheduled with delayedname()
    '''
    timeq.removeByName(name)

def listDelayed():
    '''
    Print the contents of the delayed queue.
    '''
    timeq.printQueue()

def queue(function, a=(), kw=None):
    '''
    Queue a command to be run on the very next tick. Requires a map be started
    on the server (and ticks to be firing). Args can be passed in as a tuple,
    or as keyword argments. This is like a Python-based es_soon.
    '''
    registerTicker()
    if not isinstance(a, tuple):
      a = (a,)
    q.put((function, a, kw or {}))

# end public external interfaces
# end public external interfaces
##################################


def registerTicker():
  '''
  Internal use recommended. Registers a ticklistener for the gamethread
  usage if one isn't registered.
  '''
  global tickreg
  with register_lock:
    if not tickreg:
      tickreg = True
      es.addons.registerTickListener(tick)

def unregisterTicker():
  '''
  Internal use recommended.
  Unregisters a ticklistener for the gamethread usage if one is configured.
  '''
  global tickreg
  with register_lock:
    if tickreg:
      tickreg = False
      es.addons.unregisterTickListener(tick)


def _executenode(node):
    '''
    Internal use recommended.
    Helper function to execute and then remove an item from the gameq
    '''
    function, a, kw = node.cmd
    timeq.remove(node)
    try:
        function(*a, **kw)
    finally:
        pass

# gameframe callback
def tick():
    '''
    Internal use recommended.
    '''
    # handle normal q
    while not q.empty():
        function, a, kw = q.get()
        function(*a, **kw)
    # check the first one to speed this up since none are ready unless it is.
    first = timeq.getFirst()
    if first:
        now = time.time()
        if first.gotime <= now:
            _executenode(first)
            # make a copy of the list so that we don't
            tasks = list(timeq.getList())
            for task in tasks:
                if task.gotime <= now:
                    _executenode(task)
                else:
                    break

    if timeq.empty() and q.empty():
        unregisterTicker()

