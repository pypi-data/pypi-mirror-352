import as3lib.toplevel as as3
import as3lib.configmodule as confmod
from as3lib import metaclasses
from subprocess import check_output as co
from subprocess import CalledProcessError as CPE
from typing import Union

class File:
   applicationDirectory
   applicationStorageDirectory
   cacheDirectory
   desktopDirectory
   documentsDirectory
   downloaded
   exists
   icon
   isDirectory
   isHidden
   isPackage
   isSymbolicLink
   lineEnding
   nativePath
   parent
   permissionStatus
   separator
   spaceAvailable
   systemCharset
   url
   userDirectory
   def _checkFileName():
      #windows: 
      # split off drive letter or url tag
      # check for reserved characters (<>:"/|?*)
      # file/directory names must readable characters or specific special unicode characters (ex: right to left language designator)
      # check for case to determine if it already exists (windows isn't case sensitive)
      # check if directories have a period (not allowed)
      # check for a period or space at the end of the directories and/or file (not allowed)
      # check for names CON, PRN, AUX, NUL, COM0, COM1, COM2, COM3, COM4, COM5, COM6, COM7, COM8, COM9, COM¹, COM², COM³, LPT0, LPT1, LPT2, LPT3, LPT4, LPT5, LPT6, LPT7, LPT8, LPT9, LPT¹, LPT², and LPT³ (not allowed)
      # check for above names before a file extension (not allowed)
      #linux and macos:
      # make sure file name doesn't contain a slash
      pass
   def __init__(self,path:Union[str,as3.String]):
      #!detect url path
      #!convert path to native path and url
      #!Throw exception ArguementError if path is invalid
      self._filepath = path
   #def __str__(self):
      #return the string of the native path
   def browseForDirectory():
      pass
   def browseForOpen():
      pass
   def browseForOpenMultiple():
      pass
   def browseForSave():
      pass
   def cancel():
      pass
   def canonicalize():
      pass
   def clone():
      pass
   def copyTo():
      pass
   def copyToAsync():
      pass
   def createDirectory():
      pass
   def createTempDirectory():
      pass
   def createTempFile():
      pass
   def deleteDirectory():
      pass
   def deleteDirectoryAsync():
      pass
   def deleteFile():
      pass
   def deleteFileAsync():
      pass
   def getDirectoryListing():
      pass
   def getDirectoryListingAsync():
      pass
   def getRelativePath():
      pass
   def getRootDirectories(self):
      #!Change returned values inside of the arrays into File objects
      match confmod.platform:
         case "Windows":
            drives = f"{co("fsutil fsinfo drives",shell=True)}".replace(" ","").replace("\\r","").split("Drives:")[1].replace("\\n'","").split("\\")
            tempDrives = as3.Array()
            for i in drives:
               if i == "":
                  continue
               try:
                  tempStatus = f"{co(f"fsutil fsinfo volumeinfo {i}",shell=True)}"
                  tempDrives.push(File(i))
               except CPE as e:
                  if "not ready" in f"{e.output}":
                     continue
                  tempDrives.push(File(i))
            return tempDrives
         case "Linux" | "Darwin":
            return as3.Array(File("/"))
   def moveTo():
      pass
   def moveToAsync():
      pass
   def moveToTrash():
      pass
   def moveToTrashAsync():
      pass
   def openWithDefaultApplication():
      pass
   def requestPermission():
      pass
   def resolvePath():
      pass
class FileMode(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   APPEND = "append"
   READ = "read"
   UPDATE = "update"
   WRITE = "write"
class FileStream:
   pass
class StorageVolume:
   pass
class StorageVolumeInfo:
   pass
