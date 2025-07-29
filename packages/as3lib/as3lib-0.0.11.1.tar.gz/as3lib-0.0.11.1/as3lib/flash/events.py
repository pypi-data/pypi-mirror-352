from as3lib import metaclasses
import as3lib.toplevel as as3
from copy import copy

#BaseEvent
class _AS3_BASEEVENT:
   def _getBubbles(self):
      return self.__bubbles
   bubbles = property(fget=_getBubbles)
   def _getCancelable(self):
      return self.__cancelable
   cancelable = property(fget=_getCancelable)
   def _getCTarget(self):
      return self.__currentTarget
   currentTarget = property(fget=_getCTarget)
   def _getEventPhase(self):
      return self.__eventPhase
   eventPhase = property(fget=_getEventPhase)
   def _getTarget(self):
      return self.__target
   target = property(fget=_getTarget)
   def _getType(self):
      return self.__type
   type = property(fget=_getType)
   def __init__(self,type,bubbles=False,cancelable=False,_target=None):
      if type not in self._INTERNAL_allowedTypes:
         raise Exception("Provided event type is not valid for this object")
      self.__type = type
      self.__bubbles = bubbles
      self.__cancelable = cancelable
      self.__currentTarget = None
      self.__target = _target
      self.__eventPhase = None
      self.__preventDefault = False
   def __eq__(self,value):
      return self.type == value
   def __str__(self):
      return self.type
   def getEventProperties(self):
      return (self.type,self.bubbles,self.cancelable,self.currentTarget,self.eventPhase,self.target)
   def _Internal_setTarget(self,target):
      """Internal method. do not use"""
      self.__target = target
   def _Internal_setCurrentTarget(self,currentTarget):
      """Internal method. do not use"""
      self.__currentTarget = currentTarget
      currentTarget(self.type)
   def clone(self):
      return copy(self)
   def formatToString(self,className,*arguements):...
   def isDefaultPrevented(self):
      return self.__preventDefault
   def preventDefault(self):
      if self.cancelable == True:
         self.__preventDefault = True
   def stopImmediatePropagation(self):...
   def stopPropagation(self):...
   def toString(self):
      return f"[Event type={self.type} bubbles={self.bubbles} cancelable={self.cancelable}]"

#Dummy classes
class Event(_AS3_BASEEVENT):...
class EventDispatcher:...
class TextEvent:...
class ErrorEvent:...

#Interfaces
class IEventDispatcher:
   def __init__(self):
      self.eventobjects = {}
   def addEventListener(type, listener, useCapture=False, priority=0, useWeakReference=False):
      pass
   def dispatchEvent(event):
      pass
   def hasEventListener(type):
      pass
   def removeEventListener(type, listener, useCapture=False):
      pass
   def willTrigger(type):
      pass

#Classes
class AccelerometerEvent:...
class ActivityEvent:...
class AsyncErrorEvent:...
class AudioOutputChangeEvent:...
class AVDictionaryDataEvent:...
class AVHTTPStatusEvent:...
class AVPauseAtPeriodEndEvent:...
class BrowserInvokeEvent:...
class ContextMenuEvent:...
class DataEvent:...
class DatagramSocketDataEvent:...
class DeviceRotationEvent:...
class DNSResolverEvent:...
class DRMAuthenticateEvent:...
class DRMAuthenticateCompleteEvent:...
class DRMAuthenticateErrorEvent:...
class DRMDeviceGroupErrorEvent:...
class DRMErrorEvent:...
class DRMLicenseRequestEvent:...
class DRMMetadataEvent:...
class DRMReturnVoucherCompleteEvent:...
class DRMStatusEvent:...
class ErrorEvent:...
class Event(_AS3_BASEEVENT):
   ACTIVATE = "activate" #bubbles=False, cancelable=False
   ADDED = "added" #bubbles=True, cancelable=False
   ADDED_TO_STAGE = "addedToStage" #bubbles=False, cancelable=False
   BROWSER_ZOOM_CHANGE = "browerZoomChange" #bubbles=False, cancelable=False
   CANCEL = "cancel" #bubbles=False, cancelable=False
   CHANGE = "change" #bubbles=True, cancelable=False
   CHANNEL_MESSAGE = "channelMessage" #bubbles=False, cancelable=False
   CHANNEL_STATE = "channelState" #bubbles=False, cancelable=False
   CLEAR = "clear" #bubbles=False, cancelable=False
   CLOSE = "close" #bubbles=False, cancelable=False
   CLOSING = "closing" #bubbles=False, cancelable=True
   COMPLETE = "complete" #bubbles=False, cancelable=False
   CONNECT = "connect" #bubbles=False, cancelable=False
   CONTEXT3D_CREATE = "context3DCreate" #?
   COPY = "copy" #bubbles=False, cancelable=False
   CUT = "cut" #bubbles=False, cancelable=False
   DEACTIVATE = "deactivate" #bubbles=False, cancelable=False
   DISPLAYING = "displaying" #bubbles=False, cancelable=False
   ENTER_FRAME = "enterFrame" #bubbles=False, cancelable=False
   EXIT_FRAME = "exitFrame" #bubbles=False, cancelable=False
   EXITING = "exiting" #bubbles=False, cancelable=True
   FRAME_CONSTRUCTED = "frameConstructed" #bubbles=False, cancelable=False
   FRAME_LABEL = "frameLabel" #bubbles=False, cancelable=False
   FULLSCREEN = "fullscreen" #bubbles=False, cancelable=False
   HTML_BOUNDS_CHANGE = "htmlBoundsChange" #bubbles=False, cancelable=False
   HTML_DOM_INITIALIZE = "htmlDOMInitialize" #bubbles=False, cancelable=False
   HTML_RENDER = "htmlRender" #bubbles=False, cancelable=False
   ID3 = "id3" #bubbles=False, cancelable=False
   INIT = "init" #bubbles=False, cancelable=False
   LOCATION_CHANGE = "locationChange" #bubbles=False, cancelable=False
   MOUSE_LEAVE = "mouseLeave" #bubbles=False, cancelable=False
   NETWORK_CHANGE = "networkChange" #bubbles=False, cancelable=False
   OPEN = "open" #bubbles=False, cancelable=False
   PASTE = "paste" #bubbles=(platformDependant), cancelable=False
   PREPARING = "preparing" #bubbles=False, cancelable=False
   REMOVED = "removed" #bubbles=True, cancelable=False
   REMOVED_FROM_STAGE = "removeFromStage" #bubbles=False, cancelable=False
   RENDER = "render" #bubbles=False, cancelable=False
   RESIZE = "resize" #bubbles=False, cancelable=False
   SCROLL = "scroll" #bubbles=False, cancelable=False
   SELECT = "select" #bubbles=False, cancelable=False
   SELECT_ALL = "selectAll" #bubbles=False, cancelable=False
   SOUND_COMPLETE = "soundComplete" #bubbles=False, cancelable=False
   STANDARD_ERROR_CLOSE = "standardErrorClose" #bubbles=False, cancelable=False
   STANDARD_INPUT_CLOSE = "standardInputClose" #bubbles=False, cancelable=False
   STANDARD_OUTPUT_CLOSE = "standardOutputClose" #bubbles=False, cancelable=False
   SUSPEND = "suspend" #bubbles=False, cancelable=False
   TAB_CHILDREN_CHANGE = "tabChildrenChange" #bubbles=True, cancelable=False
   TAB_ENABLE_CHANGE = "tabEnableChange" #bubbles=True, cancelable=False
   TAB_INDEX_CHANGE = "tabIndexChange" #bubbles=True, cancelable=False
   TEXT_INTERACTION_MODE_CHANGE = "textInteractionModeChange" #bubbles=False, cancelable=False
   TEXTURE_READY = "textureReady" #?
   UNLOAD = "unload" #bubbles=False, cancelable=False
   USER_IDLE = "userIdle" #bubbles=False, cancelable=False
   USER_PRESENT = "userPresent" #bubbles=False, cancelable=False
   VIDEO_FRAME = "videoFrame" #bubbles=False, cancelable=False
   WORKER_STATE = "workerState" #bubbles=False, cancelable=False
   _INTERNAL_allowedTypes = {"activate","added","addedToStage","browerZoomChange","cancel","change","channelMessage","channelState","clear","close","closing","complete","connect","context3DCreate","copy","cut","deactivate","displaying","enterFrame","exitFrame","exiting","frameConstructed","frameLabel","fullscreen","htmlBoundsChange","htmlDOMInitialize","htmlRender","id3","init","locationChange","mouseLeave","networkChange","open","paste","preparing","removed","removeFromStage","render","resize","scroll","select","selectAll","soundComplete","standardErrorClose","standardInputClose","standardOutputClose","suspend","tabChildrenChange","tabEnableChange","tabIndexChange","textInteractionModeChange","textureReady","unload","userIdle","userPresent","videoFrame","workerState"}
class EventDispatcher:
   #!Implement priority, weakReference
   def __init__(self,target:IEventDispatcher=None):
      #!Implement target
      self._events = {}
      self._eventsCapture = {}
   def addEventListener(self,type:as3.allString,listener,useCapture:as3.allBoolean=False,priority:as3.allInt=0,useWeakReference:as3.allBoolean=False):
      #!Add error
      if useCapture == False:
         if self._events.get(type) == None:
            self._events[type] = [listener]
         elif listener not in self._events[type]:
            self._events[type].append(listener)
      else:
         if self._eventsCapture.get(type) == None:
            self._eventsCapture[type] = [listener]
         elif listener not in self._eventsCapture[type]:
            self._eventsCapture[type].append(listener)
   #def _dispatchEventType(self,type_,capture=False):
   #   """
   #   This is a temporary function that will be removed later. I just have no idea how to implement the original and haven't implemented event objects yet.
   #   """
   #   if capture == False:
   #      if self._events.get(type_) != None:
   #         for i in self._events[type_]:
   #            i(type_)
   #   else:
   #      if self._eventsCapture.get(type_) != None:
   #         for i in self._eventsCapture[type_]:
   #            i(type_)
   def dispatchEvent(self,event):
      #!I do not know how to implement useCapture here
      #!Implement stuff to do with bubbles
      if event.isDefaultPrevented() == False:
         if self._events.get(event.type) != None:
            e = event.clone()
            for i in self._events[event.type]:
               e._Internal_setCurrentTarget(i)
            return True
      return False
   def hasEventListener(self,type):
      if self._events.get(type) != None or self._eventsCapture.get(type) != None:
         return True
      return False
   def removeEventListener(self,type:as3.allString,listener,useCapture:as3.allBoolean=False):
      if useCapture == False:
         if self._events.get(type) != None:
            try:
               self._events[type].remove(listener)
            except:
               pass
      else:
         if self._eventsCapture.get(type) != None:
            try:
               self._eventsCapture[type].remove(listener)
            except:
               pass
   def willTrigger(self,type:as3.allString):
      pass
class EventPhase(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   AT_TARGET = 2
   BUBBLING_PHASE = 3
   CAPTURING_PHASE = 1
class FileListEvent:...
class FocusEvent:...
class FullScreenEvent:...
class GameInputEvent:...
class GeolocationEvent:...
class GestureEvent:...
class GesturePhase:...
class HTMLUncaughtScriptExceptionEvent:...
class HTTPStatusEvent:...
class IMEEvent:...
class InvokeEvent:...
class IOErrorEvent:...
class KeyboardEvent:...
class LocationChangeEvent:...
class MediaEventEvent:...
class MouseEventEvent:...
class NativeDragEvent:...
class NativeProcessExitEvent:...
class NativeWindowBoundsEvent:...
class NativeWindowDisplayStateEvent:...
class NetDataEvent:...
class NetMonitorEvent:...
class NetStatusEvent:...
class OutputProgressEvent:...
class PermissionEvent:...
class PressAndTapGestureEvent:...
class ProgressEvent:...
class RemoteNotificationEvent:...
class SampleDataEvent:...
class ScreenMouseEvent:...
class SecurityErrorEvent:...
class ServerSocketConnectEvent:...
class ShaderEvent:...
class SoftKeyboardEvent:...
class SoftKeyboardTrigger:...
class SQLEvent:...
class SQLUpdateEvent:...
class StageOrientationEvent:...
class StageVideoAvailabilityEvent:...
class StageVideoEventEvent:...
class StatusEvent:...
class StorageVolumeChangeEvent:...
class SyncEvent:...
class TextEvent(_AS3_BASEEVENT):
   LINK = "link" #bubbles=True, cancelable=False
   TEXT_INPUT = "textInput" #bubbles=True, cancelable=True
   _INTERNAL_allowedTypes = {"link","textInput"}
   def __init__(self,type,bubbles=False,cancelable=False,text="",_target=None):
      super().__init__(type,bubbles,cancelable,_target)
      self.text=text
   def toString(self):
      return f"[TextEvent type={self.type} bubbles={self.value} cancelable={self.cancelable} text={self.text}]"
class ThrottleEvent:...
class ThrottleType:...
class TimerEvent(_AS3_BASEEVENT):
   TIMER = "timer" #bubbles=False, cancelable=False
   TIMER_COMPLETE = "timerComplete" #bubbles=False, cancelable=False
   _INTERNAL_allowedTypes = {"timer","timerComplete"}
   def __init__(self,type,bubbles=False,cancelable=False,_target=None):
      super().__init__(type,bubbles,cancelable,_target)
   def toString(self):
      return f"[TimerEvent type={self.type} bubbles={self.value} cancelable={self.cancelable}]"
   def updateAfterEvent(self):...
class TouchEvent:...
class TouchEventIntent:...
class TransformGestureEvent:...
class UncaughtErrorEvent:...
class UncaughtErrorEvents:...
class VideoEvent:...
class VideoTextureEvent:...
class VsyncStateChangeAvailabilityEvent:...
