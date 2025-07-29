import as3lib.toplevel as as3

#finish implementing everything from these classes
class DRMManagerError():
   __slots__ = ("error")
   def __init__(self, message=""):
      as3.trace(type(self), message, isError=True)
      self.error = message
class EOFError():
   __slots__ = ("error")
   def __init__(self, message=""):
      as3.trace(type(self), message, isError=True)
      self.error = message
class IllegalOperationError():
   __slots__ = ("error")
   def __init__(self, message=""):
      as3.trace(type(self), message, isError=True)
      self.error = message
class InvalidSWFError():
   __slots__ = ("error")
   def __init__(self, message=""):
      as3.trace(type(self), message, isError=True)
      self.error = message
class IOError():
   __slots__ = ("error")
   def __init__(self, message=""):
      as3.trace(type(self), message, isError=True)
      self.error = message
class MemoryError():
   __slots__ = ("error")
   def __init__(self, message=""):
      as3.trace(type(self), message, isError=True)
      self.error = message
class PermissionError():
   __slots__ = ("error")
   def __init__(self, message=""):
      as3.trace(type(self), message, isError=True)
      self.error = message
class ScriptTimeoutError():
   __slots__ = ("error")
   def __init__(self, message=""):
      as3.trace(type(self), message, isError=True)
      self.error = message
class SQLError():
   __slots__ = ("error")
   def __init__(self, message=""):
      as3.trace(type(self), message, isError=True)
      self.error = message
class SQLErrorOperation():
   __slots__ = ("error")
   def __init__(self, message=""):
      as3.trace(type(self), message, isError=True)
      self.error = message
class StackOverflowError():
   __slots__ = ("error")
   def __init__(self, message=""):
      as3.trace(type(self), message, isError=True)
      self.error = message
