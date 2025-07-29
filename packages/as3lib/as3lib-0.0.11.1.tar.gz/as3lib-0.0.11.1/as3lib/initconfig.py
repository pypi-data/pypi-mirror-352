import platform, subprocess, configparser
from . import configmodule
from pathlib import Path

if platform.system() == "Windows":
   from os import getlogin
   import ctypes
   try:
      import win32api
   except:
      configmodule.initerror.append((3,"pywin32 is required for operation on Windows but is either not installed or not accessible."))
elif platform.system() in ("Linux","Darwin"):
   from os import getuid
   from pwd import getpwuid

"""
initerrors
0 - platform not implemented
1 - function not implemented for current platform
2 - (Linux specific) unexpected display server (expected x11 or wayland)
3 - dependency not found
4 - other error
"""

def defaultTraceFilePath_Flash(versionOverride:bool=False,overrideSystem:str=None,overrideVersion:str=None):
   """
   Outputs the defualt file path for trace as defined by https://web.archive.org/web/20180227100916/helpx.adobe.com/flash-player/kb/configure-debugger-version-flash-player.html
   Since anything earlier than Windows 7 isn't supported by python 3, you normally wouldn't be able to get the file path for these systems but I have included an optional parameter to force this function to return it.
   """
   if configmodule.platform == "Windows":
      username = getlogin()
   elif configmodule.platform in {"Linux","Darwin"}:
      username = getpwuid(getuid())[0]
   if versionOverride == True:
      if overrideSystem == "Linux":
         return fr"/home/{username}/.macromedia/Flash_Player/Logs/flashlog.txt"
      elif overrideSystem == "Darwin":
         return fr"/Users/{username}/Library/Preferences/Macromedia/Flash Player/Logs/flashlog.txt"
      elif overrideSystem == "Windows":
         if overrideVersion in {"95","98","ME","XP"}:
            return fr"C:\Documents and Settings\{username}\Application Data\Macromedia\Flash Player\Logs\flashlog.txt"
         elif overrideVersion in {"Vista","7","8","8.1","10","11"}:
            return fr"C:\Users\{username}\AppData\Roaming\Macromedia\Flash Player\Logs\flashlog.txt"
   elif configmodule.platform == "Linux":
      return fr"/home/{username}/.macromedia/Flash_Player/Logs/flashlog.txt"
   elif configmodule.platform == "Windows":
      return fr"C:\Users\{username}\AppData\Roaming\Macromedia\Flash Player\Logs\flashlog.txt"
   elif configmodule.platform == "Darwin":
      return fr"/Users/{username}/Library/Preferences/Macromedia/Flash Player/Logs/flashlog.txt"

def sm_x11():
   """
   Gets and returns screen width, screen height, refresh rate, and color depth on x11
   """
   xr = f'{subprocess.check_output("xrandr --current", shell=True)}'.split("\\n")
   for option in xr:
      if option.find("*") != -1:
         curop = option.split(" ")
         break
   ops = []
   for i in curop:
      if i != "":
         ops.append(i)
   ops.pop(0)
   for i in ops:
      if i.find("*") != -1:
         temprr = i.replace("*","").replace("+","")
         break
   cdp = f'{subprocess.check_output("xwininfo -root | grep Depth", shell=True)}'.replace("\\n","").replace("b'","").replace(" ","").replace("'","").split(":")[1]
   tempwidth = f'{subprocess.check_output("xwininfo -root | grep Width", shell=True)}'.replace("\\n","").replace("b'","").replace(" ","").replace("'","").split(":")[1]
   tempheight = f'{subprocess.check_output("xwininfo -root | grep Height", shell=True)}'.replace("\\n","").replace("b'","").replace(" ","").replace("'","").split(":")[1]
   return int(tempwidth),int(tempheight),float(temprr),int(cdp)

def sm_wayland():
   return config.getint("wayland","screenwidth",fallback=1600),config.getint("wayland","screenheight",fallback=900),config.getfloat("wayland","refreshrate",fallback=60.00),config.getint("wayland","colordepth",fallback=8)

def sm_windows():
   settings = win32api.EnumDisplaySettings(win32api.EnumDisplayDevices().DeviceName, -1)
   temp = tuple(getattr(settings,i) for i in ('DisplayFrequency','BitsPerPel'))
   return int(ctypes.windll.user32.GetSystemMetrics(0)), int(ctypes.windll.user32.GetSystemMetrics(1)), float(temp[0]), int(temp[1])

def sm_darwin():
   pass

def getSeparator():
   if configmodule.platform == "Windows":
      return "\\"
   return "/"

def getDesktopDir():
   if configmodule.platform == "Linux":
      deskdir = f'{subprocess.check_output("echo $XDG_DOCUMENTS_DIR",shell=True)}'.replace("\\n","").replace("b'","").replace("'","")
      if deskdir != "":
         return deskdir
   return configmodule.userdirectory / "Desktop"

def getDocumentsDir():
   if configmodule.platform == "Linux":
      deskdir = f'{subprocess.check_output("echo $XDG_DESKTOP_DIR",shell=True)}'.replace("\\n","").replace("b'","").replace("'","")
      if deskdir != "":
         return deskdir
   return configmodule.userdirectory / "Documents"

def getdmtype():
   temp = str(subprocess.check_output("loginctl show-session $(loginctl | grep $(whoami) | awk '{print $1}') -p Type", shell=True))
   if temp[:2] == "b'" and temp[-1:] == "'":
      temp = temp[2:-1]
   for i in temp.split("\\n"):
      if len(i) > 0:
         temp2 = i.split("=")[-1]
         if temp2 in {"x11","wayland"}:
            return temp2
   return "error"

def getdmname():
   temp = str(subprocess.check_output("loginctl show-session $(loginctl | grep $(whoami) | awk '{print $1}') -p Desktop",shell=True))
   if temp[:2] == "b'" and temp[-1:] == "'":
      temp = temp[2:-1]
   for i in temp.split("\\n"):
      if len(i) > 0:
         temp2 = i.split("=")[-1]
         if len(temp2) > 0:
            return temp2.lower()
   return "error"

def dependencyCheck():
   global config
   hasDeps = True
   if configmodule.platform == "Linux":
      wmt = str(subprocess.check_output("echo $XDG_SESSION_TYPE",shell=True))[2:].replace("\\n'","")
      if wmt == "wayland":
         x=0
      else:
         try:
            subprocess.check_output("which xwininfo",shell=True)
         except:
            configmodule.initerror.append((3,"linux (xorg): requirement 'xwininfo' not found"))
            hasDeps = False
         try:
            subprocess.check_output("which xrandr",shell=True)
         except:
            configmodule.initerror.append((3,"linux (xorg): requirement 'xrandr' not found"))
            hasDeps = False
      try:
         subprocess.check_output("which bash",shell=True)
      except:
         configmodule.initerror.append((3,"linux: requirement 'bash' not found"))
         hasDeps = False
      try:
         subprocess.check_output("which awk",shell=True)
      except:
         configmodule.initerror.append((3,"linux: requirement 'awk' not found"))
         hasDeps = False
      try:
         subprocess.check_output("which whoami",shell=True)
      except:
         configmodule.initerror.append((3,"linux: requirement 'whoami' not found"))
         hasDeps = False
      try:
         subprocess.check_output("which loginctl",shell=True)
      except:
         configmodule.initerror.append((3,"linux: requirement 'loginctl' not found"))
         hasDeps = False
      try:
         subprocess.check_output("which echo",shell=True)
         if str(subprocess.check_output("echo test",shell=True)).replace("\\n","")[2:-1] != "test":
            raise
      except:
         configmodule.initerror.append((3,"linux: requirement 'echo' not found"))
         hasDeps = False
   elif configmodule.platform == "Windows":
      pass
   elif configmodule.platform == "Darwin":
      pass
   #<a href="https://pypi.org/project/numpy">numpy</a>
   #<a href="https://pypi.org/project/Pillow">Pillow</a>
   #<a href="https://pypi.org/project/tkhtmlview">tkhtmlview</a>
   config.set("dependencies","passed",str(hasDeps))
   configmodule.hasDependencies = hasDeps

def configLoader():
   configpath = configmodule.librarydirectory / "as3lib.cfg"
   if configpath.exists() == True:
      config = configparser.ConfigParser()
      config.optionxform=str
      config2 = configparser.ConfigParser()
      config2.optionxform=str
      with open(configpath, 'r') as f:
         config.read_string(f.read())
         config2.read_string(f.read())
      return config,config2
   else:
      mmcfgpath = configmodule.librarydirectory / "mm.cfg"
      wlcfgpath = configmodule.librarydirectory / "wayland.cfg"
      ErrorReportingEnable = False
      MaxWarnings = False
      TraceOutputFileEnable = False
      TraceOutputFileName = ""
      ClearLogsOnStartup = 1
      if mmcfgpath.exists() == True:
         mmcfg = configparser.ConfigParser()
         with open(mmcfgpath, 'r') as f:
            mmcfg.read_string('[dummy_section]\n' + f.read())
         ErrorReportingEnable = mmcfg.getboolean("dummy_section","ErrorReportingEnable",fallback=False)
         MaxWarnings = mmcfg.getboolean("dummy_section","MaxWarnings",fallback=False)
         TraceOutputFileEnable = mmcfg.getboolean("dummy_section","TraceOutputFileEnable",fallback=False)
         TraceOutputFileName = mmcfg.get("dummy_section","TraceOutputFileName",fallback="")
         ClearLogsOnStartup = mmcfg.getint("dummy_section","ClearLogsOnStartup",fallback=1)
      sw = 1600
      sh = 900
      rr = 60.00
      cd = 8
      if wlcfgpath.exists() == True:
         wlcfg = configparser.ConfigParser()
         with open(wlcfgpath, 'r') as f:
            wlcfg.read_string(f.read())
         sw = wlcfg.getint("Screen","screenwidth",fallback=1600)
         sh = wlcfg.getint("Screen","screenheight",fallback=900)
         rr = wlcfg.getfloat("Screen","refreshrate",fallback=60.00)
         cd = wlcfg.getint("Screen","colordepth",fallback=8)
         wlcfgpath.unlink(missing_ok=True)
      config = configparser.ConfigParser()
      config.read_string(f"[dependencies]\npassed=false\n\n[mm.cfg]\nErrorReportingEnable={ErrorReportingEnable}\nMaxWarnings={MaxWarnings}\nTraceOutputFileEnable={TraceOutputFileEnable}\nTraceOutputFileName=\"{TraceOutputFileName}\"\nClearLogsOnStartup={ClearLogsOnStartup}\nNoClearWarningNumber=0\n\n[wayland]\nscreenwidth={sw}\nscreenheight={sh}\nrefreshrate={rr}\ncolordepth={cd}")
      return config,"default"
      
config = None

def initconfig():
   #set up variables needed by mutiple modules
   global config
   configmodule.librarydirectory = Path(__file__).resolve().parent
   config,config2 = configLoader()
   configmodule.platform = platform.system()
   if config.getboolean("dependencies","passed",fallback=False) == False:
      dependencyCheck()
   configmodule.separator = getSeparator()
   configmodule.userdirectory = Path.home()
   configmodule.desktopdirectory = getDesktopDir()
   configmodule.documentsdirectory = getDocumentsDir()
   configmodule.defaultTraceFilePath = configmodule.librarydirectory / "flashlog.txt"
   configmodule.defaultTraceFilePath_Flash = defaultTraceFilePath_Flash()
   configmodule.pythonversion = platform.python_version()
   if configmodule.platform == "Linux":
      configmodule.displayserver = getdmtype()
      configmodule.dmname = getdmname()
      if configmodule.displayserver == "x11":
         configmodule.width,configmodule.height,configmodule.refreshrate,configmodule.colordepth = sm_x11()
      elif configmodule.displayserver == "wayland":
         configmodule.width,configmodule.height,configmodule.refreshrate,configmodule.colordepth = sm_wayland()
      else:
         configmodule.initerror.append((2,f"windowmanagertype \"{configmodule.windowmanagertype}\" not supported"))
   elif configmodule.platform == "Windows":
      configmodule.width,configmodule.height,configmodule.refreshrate,configmodule.colordepth = sm_windows()
   elif configmodule.platform == "Darwin":
      configmodule.initerror.append((1,"Darwin: Fetching screen properties is not implemented."))
      #configmodule.width,configmodule.height,configmodule.refreshrate,configmodule.colordepth = sm_darwin()
      ...
   elif configmodule.platform == "":
      configmodule.initerror.append((4,"Platform could not be determined"))
   else:
      configmodule.initerror.append((0,f"Current platform {configmodule.platform} not supported"))
   configmodule.ErrorReportingEnable = config.getboolean("mm.cfg","ErrorReportingEnable",fallback=False)
   configmodule.MaxWarnings = config.getboolean("mm.cfg","MaxWarnings",fallback=False)
   configmodule.TraceOutputFileEnable = config.getboolean("mm.cfg","TraceOutputFileEnable",fallback=False)
   tempTraceOutputFileName = config.get("mm.cfg","TraceOutputFileName",fallback="")
   configmodule.ClearLogsOnStartup = config.getint("mm.cfg","ClearLogsOnStartup",fallback=1)
   if configmodule.ClearLogsOnStartup == 0:
      configmodule.CurrentWarnings = config.getint("mm.cfg","NoClearWarningNumber",fallback=0)
   if tempTraceOutputFileName == "":
      tempTraceOutputFileName = configmodule.defaultTraceFilePath
   if Path(tempTraceOutputFileName).is_dir() == True:
      print("Path provided is a directory, writing to defualt location instead.")
      tempTraceOutputFileName = configmodule.defaultTraceFilePath
   configmodule.TraceOutputFileName = Path(tempTraceOutputFileName)
   if configmodule.ClearLogsOnStartup == 1:
      if configmodule.TraceOutputFileName.exists() == True:
         with open(configmodule.TraceOutputFileName, "w") as f: 
            f.write("")
   if config != config2 or config2 == "default":
      with open(configmodule.librarydirectory / "as3lib.cfg","w") as f:
         config.write(f)
   del config

   #Report errors to user
   if len(configmodule.initerror) != 0:
      print(f"Warning: as3lib has initialized with errors, some functionality may be broken.\n{''.join((f"\tType={i[0]}; Message={i[1]}\n" for i in configmodule.initerror))}")
   
   #Tell others that library has been initialized
   configmodule.initdone = True
