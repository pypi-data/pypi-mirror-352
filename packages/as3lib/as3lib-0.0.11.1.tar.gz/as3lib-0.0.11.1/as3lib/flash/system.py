from as3lib import toplevel as as3
from as3lib import configmodule, metaclasses
import platform
from typing import Union
import sys
from functools import cache

class ApplicationDomain:
    pass
class Capabilities:
    #!get actual values later
    #!document changes from original
    #!use __slots__
    def _propTrue():
        return True
    def _propFalse():
        return False
    avHardwareDisable = property(fget=_propTrue) #This is not needed so I have it set to True
    @cache
    def _getCPUBits():
        return as3.Number(platform.architecture()[0][:-3])
    cpuAddressSize = property(fget=_getCPUBits) #returns 32 (32bit system) or 64 (64bit system)
    @cache
    def _getCPUArch():
        if platform.machine() in ("x86","x86_64","AMD64"):
            return "x86"
        elif platform.machine() == "PowerPC":
            return "PowerPC"
        elif platform.machine() in ("ARM",'ARM64'):
            return "ARM"
    cpuArchitecture = property(fget=_getCPUArch) #returns "PowerPC","x86","SPARC",or "ARM"
    #hasAccessibility
    hasAudio = property(fget=_propTrue)
    #hasAudioEncoder
    #hasEmbeddedVideo
    #hasIME
    #hasMP3
    #hasPrinting
    #hasScreenBroadcast
    #hasScreenPlayback
    #hasStreamingAudio
    #hasStreamingVideo
    #hasTLS
    #hasVideoEncoder
    def _getDebug():
        return configmodule.as3DebugEnable
    isDebugger = property(fget=_getDebug)
    isEmbeddedInAcrobat = property(fget=_propFalse) #Always false because this is irelavant
    #language
    #languages
    #localFileReadDisable
    @cache
    def _getManuf():
        if configmodule.platform == "Windows":
            return "Adobe Windows"
        elif configmodule.platform == "Linux":
            return "Adobe Linux"
        elif configmodule.platform == "Darwin":
            return "Adobe Macintosh"
    manufacturer = property(fget=_getManuf)
    #maxLevelIDC
    @cache
    def _getOS():
        #!add others
        if configmodule.platform == "Windows":
            pass
        elif configmodule.platform == "Linux":
            return f"Linux {platform.release()}"
        elif configmodule.platform == "Darwin":
            pass
    os = property(fget=_getOS)
    #pixelAspectRatio
    def _getPlayerType():
        return "StandAlone"
    playerType = property(fget=_getPlayerType)
    #screenColor
    #screenDPI
    #screenResolutionX
    #screenResolutionY
    #serverString
    #supports32BitProcesses
    #supports64BitProcesses
    #touchscreenType
    @cache
    def _getVer():
        tempfv = configmodule.spoofedFlashVersion
        if configmodule.platform == "Windows":
            return f"Win {tempfv[0]},{tempfv[1]},{tempfv[2]},{tempfv[3]}"
        elif configmodule.platform == "Linux":
            return f"LNX {tempfv[0]},{tempfv[1]},{tempfv[2]},{tempfv[3]}"
        elif configmodule.platform == "Darwin":
            return f"MAC {tempfv[0]},{tempfv[1]},{tempfv[2]},{tempfv[3]}"
        elif configmodule.platform == "Android":
            return f"AND {tempfv[0]},{tempfv[1]},{tempfv[2]},{tempfv[3]}"
    version = property(fget=_getVer)
    def hasMultiChannelAudio(type:Union[str,as3.String]):
        pass
class ImageDecodingPolicy(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
    ON_DEMAND = "onDemand"
    ON_LOAD = "onLoad"
class IME:
    pass
class IMEConversionMode(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
    ALPHANUMERIC_FULL = "ALPHANUMERIC_FULL"
    ALPHANUMERIC_HALF = "ALPHANUMERIC_HALF"
    CHINESE = "CHINESE"
    JAPANESE_HIRAGANA = "JAPANESE_HIRAGANA"
    JAPANESE_KATAKANA_FULL = "JAPANESE_KATAKANA_FULL"
    JAPANESE_KATAKANA_HALF = "JAPANESE_KATAKANA_HALF"
    KOREAN = "KOREAN"
    UNKNOWN = "UNKNOWN"
class JPEGLoaderContex:
    pass
class LoaderContext:
    pass
class MessageChannel:
    pass
class MessageChannelState(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
    CLOSED = "closed"
    CLOSING = "closing"
    OPEN = "open"
class Security:
    pass
class SecurityDomain:
    pass
class SecurityPanel:
    pass
class System:
    #freeMemory
    #ime
    #privateMemory
    #totalMemory
    #totalMemoryNumber
    #useCodePage
    def disposeXML():
        pass
    def exit(code:Union[int,as3.int,as3.uint]=0):
        sys.exit(int(code))
    def gc():
        pass
    def pause():
        pass
    def pauseForGCIfCollectionImminent():
        pass
    def resume():
        pass
    def setClipboard():
        pass
class SystemUpdater:
    pass
class SystemUpdaterType(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
    DRM = "drm"
    SYSTEM = "system"
class TouchscreenType(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
    FINGER = "finger"
    NONE = "none"
    STYLUS = "stylus"
class Worker:
    pass
class WorkerDomain:
    pass
class WorkerState(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
    NEW = "new"
    RUNNING = "running"
    TERMINATED = "terminated"
