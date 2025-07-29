"""
Note to self: remove all of the things that could change outside of this library
    Display stuff should not change (as defined by the actionscript documentation)
    Things that can not be changed include things like: spoofedFlashVersion
"""
hasDependencies = False
platform = "" #Windows, Linux, or Darwin
displayserver = "" #linux (x11 or wayland) or darwin (x11 or native) only
dmname = "" #linux only, name of the program managing the display (window manager or compositor)
librarydirectory = "" #full path to as3lib (this library)
pythonversion = "" #version of python currently running
interfaceType = "" #type of interface (Tkinter, or whatever else I decide to use)
spoofedFlashVersion = [32,0,0,371] #[majorVersion,minorVersion,buildNumber,internalBuildNumber]
#Note: this is the version I chose because it was the last version of flash before adobe's timebomb
addedFeatures = False #Enables features I added to make things easier. These features change how things work so they aren't enabled by default

#toplevel
as3DebugEnable = False #(True=enabled, False=disabled) state of debug mode
ErrorReportingEnable = 0 #(1=enabled, 0=disabled) state of error reporting
MaxWarnings = 100 #maximum number of warnings until they are suppressed
TraceOutputFileEnable = 0 #(1=file, 0=console) determines whether to output "trace" to a file or to the console
TraceOutputFileName = "" #file path where error messages are stored if TraceOutputFileEnable is set to "1"
CurrentWarnings = 0 #current number of warnings
MaxWarningsReached = False #(True=yes, False=no)tells if the maximum number of warnings has been reached
ClearLogsOnStartup = 1 #(1=yes, 0=no) if set, clears logs on startup. This is the default behavior in flash
defaultTraceFilePath = "" #default file path for trace output
defaultTraceFilePath_Flash = "" #default file path for trace output in flash
appdatadirectory = None #the path to the application specific data directory (must be set by the application, should not be set by other libraries)

#flash.display
#Most of this needs to be removed
width = "" #maximum width of the display window (not implemented yet), needs to be manually set on wayland
height = "" #maximum height of the display window (not implemented yet), needs to be manually set on wayland
refreshrate = "" #refresh rate of the display window (not implemented yet), needs to be manually set on wayland
colordepth = "" #color depth of the display window (not implemented yet), needs to be manually set on wayland
windows = {} #dictionary containing all of the defined windows (not implemented yet)

#flash.filesystem
separator = ""
userdirectory = ""
desktopdirectory = ""
documentsdirectory = ""

#initcheck
initdone = False #variable to make sure this module has initialized
initerror = [] #[(errcode:int,errdesc:str),...]
