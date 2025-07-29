from as3lib import toplevel as as3
from as3lib.flash import net as fn
from as3lib.flash.events import EventDispatcher, TimerEvent
from as3lib.flash import errors
from as3lib import metaclasses
from typing import Union
import binascii
from threading import Timer as timedExec

#dummy classes
class ByteArray:...


def clearInterval():
   pass
def clearTimeout():
   pass
def describeType():
   pass
def escapeMultiByte():
   pass
def getDefinitionByName():
   pass
def getQualifiedClassName():
   pass
def getQualifiedSuperclassName():
   pass
def getTimer():
   pass
def setInterval():
   pass
def setTimeout():
   pass
def unescapeMultiByte():
   pass

class IDataInput:
   pass
class IDataOutput:
   pass

class ByteArray(bytearray):
   #!Implement slice function
   def __getBytesAvailable(self):
      return self.length - self.position
   bytesAvailable=property(fget=__getBytesAvailable)
   def __getDefObjectEncoding(self):
      return self.__defObjEncode
   def __setDefObjectEncoding(self,value):
      if value in (fn.ObjectEncoding.AMF0,fn.ObjectEncoding.AMF3):
         self.__defObjEncode = value
   defaultObjectEncoding=property(fget=__getDefObjectEncoding,fset=__setDefObjectEncoding)
   def __getEndian(self):
      return Endian.BIG_ENDIAN #!placeholder
   def __setEndian(self):...
   endian=property(fget=__getEndian,fset=__setEndian)
   def __getLength(self):
      return len(self)
   def __setLength(self,value:int):
      if value > self.length:
         for i in range(value-self.length):
            self += b"\x00"
      elif value < self.length:
         self = self[:-(self.length-value)]
   length=property(fget=__getLength,fset=__setLength)
   def __getObjectEncoding(self):
      return self.__ObjEncode
   def __setObjectEncoding(self,value):
      if value in (fn.ObjectEncoding.AMF0,fn.ObjectEncoding.AMF3):
         self.__ObjEncode = value
   objectEncoding=property(fget=__getObjectEncoding,fset=__setObjectEncoding)
   def __getPosition(self):
      return self.__position
   def __setPosition(self,value):
      #!Add error when out of range
      if value >= 0 and value <= self.length:
         self.__position = value
   position=property(fget=__getPosition,fset=__setPosition)
   def __getSharable(self):
      return self.__sharable
   def __setSharable(self,value:bool):
      self.__sharable = value
   shareable=property(fget=__getSharable,fset=__setSharable)
   def _convertPythonToOutput(self,value,format=0):
      """
      Converts a python value to various formats. Only convert one byte at a time.
      Arguements:
         value - the value
         format - the format in which the value is in
            0 (default) is a flash value - int (-128,127)
            1 is the hex value as a string
            2 is the hex value as a bytes object
      """
      if format == 0:
         return value-128
      elif format == 1:
         return hex(value)
      elif format == 2:
         v = str(hex(value))[2:]
         if len(v)%2 == 1:
            v = f"0{v}"
         return binascii.unhexlify(v)
   def _convertToPythonInput(self,value,format):
      """
      Converts various formats into the format python expects for bytearrays. Only convert one byte at a time.
      Arguements:
         value - the value
         format - the format in which the value is in
            0 is a flash input - int (-128,127)
            1 is a hex value in any of the following formats: string, bytearray, bytes, ByteArray (this class).
            2 is "detect" - detects the format the byte is in and converts it. Obviously slower than explicitly stating the format.
      """
      if format == 0:
         return value+128
      elif format == 1:
         if isinstance(value,(bytearray,bytes)):
            return int(binascii.hexlify(value),16)
         else:
            return int(value,16)
      elif format == 2:
         if isinstance(value,(int,as3.int)):
            return value+128
         elif isinstance(value,(bytearray,bytes)):
            return int(binascii.hexlify(value),16)
         else:
            return int(value,16)
   def __init__(self,*args):
      super().__init__(self,*args)
      self.defaultObjectEncoding = fn.ObjectEncoding.AMF3
      self.objectEncoding = self.defaultObjectEncoding
      self.position = 0
   def __setitem__(self,item,value):
      super().__setitem__(item,self._convertToPythonInput(value,2))
   def __str__(self):
      return str(binascii.hexlify(self))[2:-1]
   def __repr__(self):
      return f"ByteArray({str(binascii.hexlify(self))[2:-1]})"
   def _writeNoEOFProtect(self,byte):
      if self.length == self.position:
         self += b"\x00"
      self[self.position] = byte
      self.position += 1
   def _multiByteWriteNoEOFProtect(self,bytes:list|tuple|as3.Array):
      for i in bytes:
         self._writeNoEOFProtect(i)
   def atomicCompareAndSwapIntAt():
      pass
   def atomicCompareAndSwapLengthAt(self,expectedLength:int,newLength:int):
      """
      In a single atomic operation, compares this byte array's length with a provided value and, if they match, changes the length of this byte array.

      This method is intended to be used with a byte array whose underlying memory is shared between multiple workers (the ByteArray instance's shareable property is true). It does the following:

         1) Reads the integer length property of the ByteArray instance
         2) Compares the length to the value passed in the expectedLength argument
         3) If the two values are equal, it changes the byte array's length to the value passed as the newLength parameter, either growing or shrinking the size of the byte array
         4) Otherwise, the byte array is not changed

      All these steps are performed in one atomic hardware transaction. This guarantees that no operations from other workers make changes to the contents of the byte array during the compare-and-resize operation.

      Parameters
         expectedLength:int — the expected value of the ByteArray's length property. If the specified value and the actual value match, the byte array's length is changed.      
         newLength:int — the new length value for the byte array if the comparison succeeds
      Returns
         int — the previous length value of the ByteArray, regardless of whether or not it changed 
      """
      #self.length = newLength if self.length == expectedLength else self.length
      if self.length == expectedLength:
         self.length = newLength
   def clear(self):
      "Clears the contents of the byte array and resets the length and position properties to 0. Calling this method explicitly frees up the memory used by the ByteArray instance."
      self.position = 0
      self = self[:0]
   def compress():
      pass
   def deflate():
      pass
   def inflate():
      pass
   def readBoolean(self):
      if self.bytesAvailable == 0:
         errors.IOError("placeholderText")
      else:
         self.position += 1
         if self[self.position-1] == 0:
            return False
         return True
   def readByte(self):
      if self.bytesAvailable == 0:
         errors.IOError("placeholderText")
      else:
         self.position += 1
         return self[self.position-1]-128
   def readBytes(self,bytes:ByteArray,offset=0,length=0):
      #!Implement default behavior of arguements, implement error, position move
      if self.bytesAvailable < length:
         errors.IOError("placeholderText")
      elif False:... #!RangeError when offset+length > length of uint
      else:
         byte[offset:offset+length] = self[self.position:self.position+length]
   def readDouble():...
   def readFloat():...
   def readInt(self):
      if self.bytesAvailable > 4:
         errors.IOError("placeholderText")
      else:
         self.position += 4
         return int(binascii.hexlify(self[self.position-4:self.position]),16)-2147483648
   def readMultiByte():...
   def readObject():...
   def readShort(self):
      if self.bytesAvailable > 2:
         errors.IOError("placeholderText")
      else:
         self.position += 2
         return int(binascii.hexlify(self[self.position-2:self.position]),16)-32768
   def readUnsignedByte(self):
      if self.bytesAvailable == 0:
         errors.IOError("placeholderText")
      else:
         self.position += 1
         return self[self.position-1]
   def readUnsignedInt(self):
      if self.bytesAvailable > 4:
         errors.IOError("placeholderText")
      else:
         self.position += 4
         return int(binascii.hexlify(self[self.position-4:self.position]),16)
   def readUnsignedShort(self):
      if self.bytesAvailable > 2:
         errors.IOError("placeholderText")
      else:
         self.position += 2
         return int(binascii.hexlify(self[self.position-2:self.position]),16)-32768
   def readUTF():...
   def readUTFBytes():...
   def toJSON(self,k:str):
      """
      Provides an overridable method for customizing the JSON encoding of values in an ByteArray object.

      The JSON.stringify() method looks for a toJSON() method on each object that it traverses. If the toJSON() method is found, JSON.stringify() calls it for each value it encounters, passing in the key that is paired with the value.

      ByteArray provides a default implementation of toJSON() that simply returns the name of the class. Because the content of any ByteArray requires interpretation, clients that wish to export ByteArray objects to JSON must provide their own implementation. You can do so by redefining the toJSON() method on the class prototype.

      The toJSON() method can return a value of any type. If it returns an object, stringify() recurses into that object. If toJSON() returns a string, stringify() does not recurse and continues its traversal.

      Parameters
         k:String — The key of a key/value pair that JSON.stringify() has encountered in its traversal of this object

      Returns
         * — The class name string. 
      """
      return "ByteArray"
   def toString(self):
      """
      Converts the byte array to a string. If the data in the array begins with a Unicode byte order mark, the application will honor that mark when converting to a string. If System.useCodePage is set to true, the application will treat the data in the array as being in the current system code page when converting
      """
      return str(binascii.hexlify(self))[2:-1]
   def uncompress():
      pass
   def __ConvBoolToByte(self,value:bool):
      if value != None:
         if value:
            return -127
         return -128
   def writeBoolean(self,value:bool):
      self._writeNoEOFProtect(self.__ConvBoolToByte(value)+128)
   def writeByte(self,value:int):...
   def writeBytes():...
   def writeDouble():...
   def writeFloat():...
   def writeInt(self,value):...
   def writeMultiByte():...
   def __writeImproperObjName(self,string):
      self._writeNoEOFProtect(hex(len(string)*2+1)[2:])
      ...
   def __writeProperObjName(self,string):
      ...
   def writeObject(self,object:dict):
      """
      Due to how this must be implemented and the fact that python does not store object names at runtime, object (and any objects that it contains) must be a dictionary. The dictionary can be formatted exactly like the object originally would be in actionscript.
      """
      self._writeNoEOFProtect("0A")
      ...
      self._writeNoEOFProtect("01")
   def writeShort():...
   def writeUnsignedInt():...
   def __utfchartobyte(self,string):...
   def writeUTF():...
   def writeUTFBytes():...

class CompressionAlgorithm(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   DEFLATE = "deflate"
   LZMA = "lzma"
   ZLIB = "zlib"
class Dictionary(dict):
   def __init__(self,weakKeys:as3.allBoolean=False):
      return super().__init__()
   def __getitem__(self,item):
      return self.get(item) #I think this is how actionscript does it but I'm not sure
   def toJSON(self,k:as3.allString):
      return "Dictionary"
class Endian(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   BIG_ENDIAN = "bigEndian"
   LITTLE_ENDIAN = "littleEndian"
class Timer(EventDispatcher):
   def __getCCount(self):
      return self.__currentCount
   currentCount=property(fget=__getCCount)
   def __getDelay(self):
      return self.__delay
   def __setDelay(self,number_ms:as3.allNumber):
      if self.running:
         self.stop()
         self.__delay = number_ms
         self.start()
      else:
         self.__delay = number_ms
   delay=property(fget=__getDelay,fset=__setDelay)
   def __getRCount(self):
      return self.__repeatCount
   def __setRCount(self,number:as3.allInt):
      self.__repeatCount = number
   repeatCount=property(fget=__getRCount,fset=__setRCount)
   def __getRunning(self):
      return self.__running
   running=property(fget=__getRunning)
   def __TimerTick(self):
      self.__currentCount += 1
      self.dispatchEvent(self.timer)
      if self.currentCount >= self.repeatCount:
         self.dispatchEvent(self.timerComplete)
      else:
         self.__timer = timedExec(self.delay/1000,self.__TimerTick)
         self.__timer.start()
   def __init__(self,delay:as3.allNumber,repeatCount:as3.allInt=0):
      super().__init__()
      self.__currentCount = 0
      self.__delay = delay
      self.repeatCount = repeatCount
      self.__running = False
      self.timer = TimerEvent("timer",False,False,self)
      self.timerComplete = TimerEvent("timerComplete",False,False,self)
   def reset(self):
      self.stop()
      self.__currentCount = 0
   def start(self):
      if self.running == False:
         self.__timer = timedExec(self.delay/1000,self.__TimerTick)
         self.__running = True
         self.__timer.start()
   def stop(self):
      if self.running == True:
         self.__timer.cancel()
         self.__running = False
