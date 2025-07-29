from as3lib import configmodule,metaclasses
import as3lib.toplevel as as3
from typing import Union
import tkinter
from typing import Generator, Any
from as3.flash.events import EventDispatcher

#Dummy classes
class InteractiveObject:...

def _winNameGen()-> Generator[int,None,None]:
   i = 0
   while True:
      yield i
      i += 1

_windowNameGenerator: Generator[int,None,None] = _winNameGen()

class as3totk:
   def anchors(flashalign:as3.allString):
      match flashalign:
         case "B":
            return "s"
         case "BL":
            return "sw"
         case "BR":
            return "se"
         case "L":
            return "w"
         case "R":
            return "e"
         case "T":
            return "n"
         case "TL":
            return "nw"
         case "TR":
            return "ne"

class ActionScriptVersion(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   ACTIONSCRIPT2 = 2
   ACTIONSCRIPT3 = 3
class AVLoader:
   pass
class AVM1Movie:
   pass
class Bitmap:
   pass
class BitmapData:
   pass
class BitmapDataChannel:
   pass
class BitmapEncodingColorSpace(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   COLORSPACE_4_2_0 = "4:2:0"
   COLORSPACE_4_2_2 = "4:2:2"
   COLORSPACE_4_4_4 = "4:4:4"
   COLORSPACE_AUTO = "auto"
class BlendMode(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   ADD = "add"
   ALPHA = "alpha"
   DARKEN = "darken"
   DIFFERENCE = "difference"
   ERASE = "erase"
   HARDLIGHT = "hardlight"
   INVERT = "invert"
   LAYER = "layer"
   LIGHTEN = "lighten"
   MULTIPLY = "multiply"
   NORMAL = "normal"
   OVERLAY = "overlay"
   SCREEN = "screen"
   SHADER = "shader"
   SUBTRACT = "subtract"
class CapsStyle(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   NONE = "none"
   ROUND = "round"
   SQUARE = "square"
class ColorCorrection(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   DEFAULR = "default"
   OFF = "off"
   ON = "on"
class ColorCorrectionSupport(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   DEFAULT_OFF = "defaultOff"
   DEFAULT_ON = "defualtOn"
   UNSUPPORTED = "unsupported"
class DisplayObject(EventDispatcher):...
class DisplayObjectContainer(InteractiveObject):...
class FocusDirection(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   BOTTOM = "bottom"
   NONE = "none"
   TOP = "top"
class FrameLabel:
   pass
class GradientType(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   LINEAR = "linear"
   RADIAL = "radial"
class Graphics:
   pass
class GraphicsBitmapFill:
   pass
class GraphicsEndFill:
   pass
class GraphicsGradientFill:
   pass
class GraphicsPath:
   pass
class GraphicsPathCommand:
   pass
class GraphicsPathWinding:
   pass
class GraphicsShaderFill:
   pass
class GraphicsSolidFill:
   pass
class GraphicsStroke:
   pass
class GraphicsTrianglePath:
   pass
class GraphicsObject:
   pass
class InteractiveObject(DisplayObject):...
class InterpolationMethod(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   LINEAR_RGB = "linearRGB"
   RGB = "rgb"
class JointStyle(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   BEVEL = "bevel"
   MITER = "miter"
   ROUND = "round"
class JPEGEncoderOptions:
   pass
class JPEGCREncoderOptions:
   pass
class LineScaleMode(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   HORIZONTAL = "horizontal"
   NONE = "none"
   NORMAL = "normal"
   VERTICAL = "vertical"
class Loader:
   pass
class LoderInfo:
   pass
class MorphShape:
   pass
class MovieClip:
   pass
class NativeMenu:
   pass
class NativeMenuItem:
   pass
class NativeWindow:
   """
   Due to limitations in tkinter, any window that isn't the main window will not be able to start out inactive. It will instead start out minimized.
   """
   def _setActive(self,state:as3.allBoolean):
      self.__active = state
   def _getActive(self):
      return self.__active
   active = property(fget=_getActive,fset=_setActive)
   #alwaysInFront
   #bounds
   def _setClosed(self,state:as3.allBoolean):
      self.__closed = state
   def _getClosed(self):
      return self.__closed
   closed = property(fget=_getClosed,fset=_setClosed)
   #displayState
   #height
   #isSupported
   #maximizable
   #maxSize
   #menu
   #minimizable
   #minSize
   #owner
   #renderMode
   #resizable
   #stage
   #supportsMenu
   #supportsNotification
   #supportsTransparency
   #systemChrome
   #systemMaxSize
   #systemMinSize
   #title
   #transparent
   #type
   #visible
   #width
   #x
   #y
   def __init__(initOptions:NativeWindowInitOptions = NativeWindowInitOptions()):
      self.__mainwindow = len(configmodule.windows) == 0:
      if self.__mainwindow == True:
         self.__windowObject = tkinter.Tk()
      else:
         self.__windowObject = tkinter.Toplevel()
         self.minimize()
      configmodule.windows[next(_windowNameGenerator)] = self
   def activate():
      if self.active == False and self.closed == False:
         if self.__mainwindow == False:
            self.maximize()
         else:
            self.__windowObject.mainloop()
         self.active = True
   def close():
      self.__windowObject.destroy()
      self.closed = True
   def globalToScreen(globalPoint): #accepts flash.geom.Point objects
      pass
   def listOwnedWindows():
      pass
   def maximize():
      pass
   def minimize():
      pass
   def notifyUser(type):
      pass
   def orderInBackOf(window:NativeWindow):
      pass
   def orderInFrontOf(window:NativeWindow):
      pass
   def orderToBack():
      pass
   def orderToFront():
      pass
   def restore():
      pass
   def startMove():
      pass
   def startResize(edgeOfCorner):
      pass
class NativeWindowDisplayState(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   MAXIMIZED = "maximized"
   MINIMIZED = "minimized"
   NORMAL = "normal"
class NativeWindowInitOptions:
   #!Add restraints for properties and make them actual properties
   def __init__(self,**kwargs):
      self.maximizable:as3.allBoolean = kwargs.get('maximizable', True)
      self.minimizable:as3.allBoolean = kwargs.get('minimizable', True)
      self.owner:NativeWindow = kwargs.get('owner', as3.null)
      self.renderMode:as3.allString = kwargs.get('renderMode')
      self.resizable:as3.allBoolean = kwargs.get('resizable', True)
      self.systemChrome:as3.allString = kwargs.get('systemChrome', NativeWindowSystemChrome.STANDARD)
      self.transparent:as3.allBoolean = kwargs.get('transparent', False)
      self.type:as3.allString = kwargs.get('type', NativeWindowType.NORMAL)
class NativeWindowRenderMode(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   AUTO = "auto"
   CPU = "cpu"
   DIRECT = "direct"
   GPU = "gpu"
class NativeWindowResize(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   BOTTOM = "B"
   BOTTOM_LEFT = "BL"
   BOTTOM_RIGHT = "BR"
   LEFT = "L"
   RIGHT = "R"
   TOP = "T"
   TOP_LEFT = "TL"
   TOP_RIGHT = "TR"
class NativeWindowSystemChrome(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   ALTERNATE = "alternate"
   NONE = "none"
   STANDARD = "standard"
class NativeWindowType(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   LIGHTWEIGHT = "lightweight"
   NORMAL = "normal"
   UTILITY = "utility"
class PixelSnapping(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   ALWAYS = "always"
   AUTO = "auto"
   NEVER = "never"
class PNGEncoderOptions:
   pass
class Scene:
   pass
class SceneMode:
   pass
class Screen:
   pass
class ScreenMode(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   colorDepth = configmodule.colordepth
   height = configmodule.height
   refreshRate = configmodule.refreshrate
   width = configmodule.width
class Shader:
   pass
class ShaderData:
   pass
class ShaderInput:
   pass
class ShaderJob:
   pass
class ShaderParameter:
   pass
class ShaderParameterType(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   BOOL = "bool"
   BOOL2 = "bool2"
   BOOL3 = "bool3"
   BOOL4 = "bool4"
   FLOAT = "float"
   FLOAT2 = "float2"
   FLOAT3 = "float3"
   FLOAT4 = "float4"
   INT = "int"
   INT2 = "int2"
   INT3 = "int3"
   INT4 = "int4"
   MATRIX2X2 = "matrix2x2"
   MATRIX3X3 = "matrix3x3"
   MATRIX4X4 = "matrix4x4"
class ShaderPrecision(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   FAST = "fast"
   FULL = "full"
class Shape:
   pass
class SimpleButtom:
   pass
class SpreadMethod(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   PAD = "pad"
   REFLECT = "reflect"
   REPEAT = "repeat"
class Sprite:
   pass
class Stage:
   pass
class Stage3D:
   pass
class StageAlign(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   BOTTOM = "B"
   BOTTOM_LEFT = "BL"
   BOTTOM_RIGHT = "BR"
   LEFT = "L"
   RIGHT = "R"
   TOP = "T"
   TOP_LEFT = "TL"
   TOP_RIGHT = "TR"
class StageAspectRatio(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   ANY = "any"
   LANDSCAPE = "landscape"
   PORTRAIT = "portrait"
class StageDisplayState(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   FULL_SCREEN = "fullScreen"
   FULL_SCREEN_INTERACTIVE = "fullScreenInteractive"
   NORMAL = "normal"
class StageOrientation(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   DEFAULT = "default"
   ROTATED_LEFT = "rotatedLeft"
   ROTATED_RIGHT = "rotatedRight"
   UNKNOWN = "unknown"
   UPSIDE_DOWN = "upsideDown"
class StageQuality(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   BEST = "best"
   HIGH = "high"
   HIGH_16X16 = "16x16"
   HIGH_16X16_LINEAR = "16x16linear"
   HIGH_8X8 = "8x8"
   HIGH_8X8_LINEAR = "8x8linear"
   LOW = "low"
   MEDIUM = "medium"
class StageScaleMode(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   EXACT_FIT = "exactFit"
   NO_BORDER = "noBorder"
   NO_SCALE = "noScale"
   SHOW_ALL = "showAll"
class SWFVersion(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   FLASH1 = 1
   FLASH2 = 2
   FLASH3 = 3
   FLASH4 = 4
   FLASH5 = 5
   FLASH6 = 6
   FLASH7 = 7
   FLASH8 = 8
   FLASH9 = 9
   FLASH10 = 10
   FLASH11 = 11
class TriangleCulling(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   NEGATIVE = "negative"
   NONE = "none"
   POSITIVE = "positive"
