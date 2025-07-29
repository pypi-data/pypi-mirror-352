import as3lib.toplevel as as3
from as3lib import configmodule as confmod
from typing import Union
from as3lib.flash.events import Event, EventDispatcher #, HTTPStatusEvent, IOErrorEvent, PermissionEvent, ProgressEvent, SecurityErrorEvent, DataEvent
from as3lib import metaclasses
from tkinter import filedialog
import as3lib.flash.utils as utils

def getClassByAlias(aliasName:as3.allString):...
def navigateToURL(request,window:as3.allString=None):...
def registerClassAlias(aliasName:as3.allString,classObject):...
def sendToURL(request):...

class DatagramSocket:...
class FileFilter:
   def __init__(self,description:Union[str,as3.String],extension:Union[str,as3.String],macType:Union[str,as3.String]=None):
      self.description = description
      self.extension = extension
      self.macType = macType
   def extensionsToArray(self):
      return as3.Array(*self.extension.split(";"))
   def macTypeToArray(self):
      if self.macType != None:
         return as3.Array(*self.macType.split(";"))
   def toTkTuple(self):
      return (self.description,self.extension.split(";"))
class FileReference(EventDispatcher):
   @staticmethod
   def _getPerStat():
      return True
   permissionStatus = property(fget=_getPerStat)
   def __init__(self):
      super().__init__()
      #self.creationDate
      #self.creator
      #self.data
      #self.extension
      #self.modificationDate
      #self.name
      #self.size
      #self.type
      self._location = None
      #!Most of these events need extra information
      self.cancel = Event("cancel",False,False,self)
      self.complete = Event("complete",False,False,self)
      #self.httpResponseStatus = HTTPStatusEvent("httpResponseStatus",False,False,self)
      #self.httpStatus = HTTPStatusEvent("httpStatus",False,False,self)
      #self.ioError = IOErrorEvent("ioError",False,False,self)
      self.open = Event("open",False,False,self)
      #self.permissionStatus = PermissionEvent("permissionStatus",False,False,self)
      #self.progress = ProgressEvent("progress",False,False,self)
      #self.securityError = SecurityErrorEvent("securityError",False,False,self)
      self.select = Event("select",False,False,self)
      #self.uploadCompleteData = DataEvent("uploadCompleteEvent",False,False,self)
   def _setFile(self,file):
      #Sets the file and all of its details
      ...
   def browse(self,typeFilter:Union[as3.Array,list,tuple]=None):
      #typeFilter is an Array/list/tuple of FileFilter objects
      if typeFilter != None:
         filename = filedialog.askopenfilename(title="Select a file to upload",filetypes=tuple(i.toTkTuple() for i in typeFilter))
      else:
         filename = filedialog.askopenfilename(title="Select a file to upload")
      try:
         return True
      except:
         print("You somhow messed it up")
      finally:
         if filename in (None,()):
            self.dispatchEvent(self.cancel)
         else:
            self.dispatchEvent(self.select)
   def cancel(self):
      pass
   def dowload(self,request,defaultFileName=None):
      pass
   def load(self):
      pass
   def requestPermission(self):
      pass
   def save(self,data,defaultFileName=None):
      #!add check for blacklisted characters  / \ : * ? " < > | %
      file = defaultFileName.split(".")
      savetype = 0 # 1=UTF-8 2=XML 3=ByteArray
      if data == None:
         as3.ArguementError("Invalid Data")
         return False
      elif isinstance(data,str):
         #write a UTF-8 text file
         savetype = 1
      #elif type(data) == #XML:
         #Write as xml format text file with format preserved
         #savetype = 2
      elif isinstance(data,utils.ByteArray):
         #write data to file as is (in byte form)
         savetype = 3
      else:
         #convert to string and save as text file. If it fails throw ArguementError
         try:
            data = str(data)
         except:
            as3.ArguementError("Invalid Data")
            return False
      if len(file) == 1:
         #no extension
         filename = filedialog.asksaveasfilename(title="Select location for download")
      else:
         #extension
         #!doesn't seen to work
         ext = f".{file[-1]}"
         filename = filedialog.asksaveasfilename(title="Select location for download",defaultextension=ext)
      try:
         return True
      except:
         print("You somhow messed it up")
      finally:
         if filename in (None,()):
            self.dispatchEvent(self.cancel)
         else:
            self.dispatchEvent(self.select)
            self._location = filename
            self.dispatchEvent(self.complete)
   def upload(self,request,uploadDataFieldName,testUpload=False):
      pass
   def uploadUnencoded(self,request):
      pass
class FileReferenceList:...
class GroupSpecifier:...
class InterfaceAddress:
   #address = classmethod()
   #broadcast = classmethod()
   def __getAddrType():
      pass
   #ipVersion = classmethod(fget=__AddrType)
   #prefixLength = classmethod()
class IPVersion(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   IPV4 = "IPv4"
   IPV6 = "IPv6"
class LocalConnection:...
class NetGroup:...
class NetGroupInfo:...
class NetGroupReceiveMode:...
class NetGroupReplicationStrategy:...
class NetGroupSendMode:...
class NetGroupSendResult:...
class NetMonitor:...
class NetStream:...
class NetStreamAppendBytesAction:...
class NetStreamInfo:...
class NetStreamMulticastInfo:...
class NetStreamPlayOptions:...
class NetStreamPlayTransitions:...
class NetworkInfo:...
class NetworkInterface:...
class ObjectEncoding(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   AMF0 = 0
   AMF3 = 3
   DEFAULT = 3
class Responder:...
class SecureSocket:...

class sodata:
   def __init__(self):
      return None
   def __str__(self):
      return f"{vars(self)}"
   def __repr__(self):
      return f"{vars(self)}"
   def toDict(self):
      return dict(vars(self))
class _AMFCODEC:
   class AMF0:
      number=b"\x00"
      boolean=b"\x01"
      string=b"\x02"
      object=b"\x03"
      movieclip=b"\x04"
      null=b"\x05"
      undefined=b"\x06"
      reference=b"\x07"
      ecma_array=b"\x08"
      object_end="b\x09"
      strict_array=b"\x0A"
      date=b"\x0B"
      long_string=b"\x0C"
      unsupported=b"\x0D"
      recordset=b"\x0E"
      xml_document=b"\x0F"
      typed_object=b"\x10"
      avmplus_object=b"\x11"
      number=b"\x00"
      number=b"\x00"
      number=b"\x00"
   class AMF3:
      undefined=b"\x00"
      null=b"\x01"
      false=b"\x02"
      true=b"\x03"
      integer=b"\x04"
      double=b"\x05"
      string=b"\x06"
      xml=b"\x07"
      date=b"\x08"
      array=b"\x09"
      object=b"\x0A"
      xml=b"\x0B"
      byte_array=b"\x0C"
      vector_int=b"\x0D"
      vector_uint=b"\x0E"
      vector_double=b"\x0F"
      vector_object=b"\x10"
      dictionary=b"\x11"

class SharedObject:
   def __init__(self):
      self._name = ""
      self._path = ""
      self.data = sodata()
   def clear(self):
      #self._name = ""
      #self._path = ""
      self.data = sodata()
   def close(self):
      pass
   def connect(self):
      pass
   def flush(slef,minDiskSpace=0):
      pass
   def getLocal(self,name,localPath=None,secure=False):
      #gets local shared object; if object exists, set path and load it. if not, just set path
      #!fix separators and make paths "Path" objects
      parent = ""
      directory = f"{confmod.separator}"
      #localPath is the path (without the file name) with the application specific data directory as root
      #   application data directory is configmodule.appdatadirectory and needs to be set manually using toplevel.setDataDirectory(directory)
      #   (implementation specific addition) if the application data directory is not specified, the library directory is used as a default
      #name is the name of the file excluding the extension because it will always be .sol
      if localPath != None:
         directory = localPath
      if confmod.appdatadirectory == None:
         #use confmod.librarydirectory
         parent = confmod.librarydirectory
      else:
         #use confmod.appdatadirectory
         parent = confmod.appdatadirectory
      if parent[-1] == confmod.separator:
         parent = parent[:-1]
      if directory[0] == confmod.separator:
         directory = directory[1:]
      if directory[-1] == confmod.separator:
         directory = directory[:-1]
      self._path = f"{parent}{confmod.separator}{directory}{confmod.separator}{name}.sol"
      self._name = name
      pass
   def getRemote(self,name,remotePath=None,persistance=False,secure=False):
      pass
   def send(self,*arguments):
      pass
   def setDirty(self,propertyName):
      pass
   def setProperty(self,propertyName,value=None):
      pass
class SharedObjectFlushStatus(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   FLUSHED = "flushed"
   PENDING = "pending"
class Socket:...
class URLLoader:...
class URLLoaderDataFormat:...
class URLRequest:...
class URLRequestDefaults:...
class URLRequestHeader:...
class URLRequestMethod:...
class URLStream:...
class URLVariables:...
class XMLSocket:...

if __name__ == "__main__":
   def eventCancel(event=None):
      print("cancel")
   def eventSelect(event=None):
      print("select")
   def eventComplete(event=None):
      print("complete")
   filter1 = FileFilter("Text File","*.txt")
   filter2 = FileFilter("Shell Script","*.sh")
   filter3 = FileFilter("Files","*.xml;*.exe;*.py")
   fr = FileReference()
   fr.addEventListener(Event.CANCEL,eventCancel)
   fr.addEventListener(Event.SELECT,eventSelect)
   fr.addEventListener(Event.COMPLETE,eventComplete)
   fr.browse([filter1,filter2,filter3])
   fr.save("test","test.txt")
