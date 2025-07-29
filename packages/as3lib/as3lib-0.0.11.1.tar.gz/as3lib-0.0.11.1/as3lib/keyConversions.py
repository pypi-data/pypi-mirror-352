from as3lib import configmodule, toplevel
import re
from typing import Union

def mouseButtonNameToTkname(name:Union[str, toplevel.String]):
   if configmodule.platform == "Linux":
      return Linux.mouseButtonNameToTkname(name)
   elif configmodule.platform == "Windows":
      return Windows.mouseButtonNameToTkname(name)
   elif configmodule.platform == "Darwin":
      pass
def tkeventToMouseButtonName(event):
   if configmodule.platform == "Linux":
      return Linux.tkeventToMouseButtonName(event)
   elif configmodule.platform == "Windows":
      return Windows.tkeventToMouseButtonName(event)
   elif configmodule.platform == "Darwin":
      pass
def tkeventToJavascriptKeycode(event):
   if configmodule.platform == "Linux":
      return Linux.tkeventToJavascriptKeycode(event)
   elif configmodule.platform == "Windows":
      return Windows.tkeventToJavascriptKeycode(event)
   elif configmodule.platform == "Darwin":
      pass
class Linux:
   def mouseButtonNameToTkname(name:Union[str, toplevel.String]):
      if name == "Left":
         return "<Button-1>"
      elif name == "Middle":
         return "<Button-2>"
      elif name == "Right":
         return "<Button-3>"
   def tkeventToMouseButtonName(event):
      if event.num == 1:
         return "Left"
      elif event.num == 2:
         return "Middle"
      elif event.num == 3:
         return "Right"
   def tkeventToJavascriptKeycode(event):
      return (None,None,None,None,None,None,None,None,None,27,49,50,51,52,53,54,55,56,57,48,189,187,8,9,81,87,69,82,84,89,85,73,79,80,219,221,13,17,65,83,68,70,71,72,74,75,76,186,222,192,16,220,90,88,67,86,66,78,77,188,190,191,16,106,18,32,20,112,113,114,115,116,117,118,119,120,121,144,145,103,104,105,109,100,101,102,107,97,98,99,96,110,None,None,None,122,123,None,None,None,None,None,None,None,13,17,111,None,18,None,36,38,33,37,39,35,40,34,45,46,None,None,None,None,None,None,None,19)[event.keycode]
class Windows:
   def mouseButtonNameToTkname(name:Union[str, toplevel.String]):
      if name == "Left":
         return
      elif name == "Middle":
         return
      elif name == "Right":
         return
   def tkeventToMouseButtonName(event):
      if event.num == 1:
         return
      elif event.num == 2:
         return
      elif event.num == 3:
         return
   def tkeventToJavascriptKeycode(event):
      #!This could possibly just be "return event.keycode" because all values are the same
      return (None,None,None,None,None,None,None,None,8,9,None,None,None,13,None,None,16,17,18,19,20,None,None,None,None,None,None,27,None,None,None,None,32,33,34,35,36,37,38,39,40,None,None,None,None,45,46,None,48,49,50,51,52,53,54,55,56,57,None,None,None,None,None,None,None,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,None,None,None,None,96,97,98,99,100,101,102,103,104,105,106,107,None,109,110,111,112,113,114,115,116,117,118,119,120,121,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,144,145,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,186,187,188,189,190,191,192,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,219,220,221,222)[event.keycode]
class Darwin_X11:
   def mouseButtonNameToTkname(name:Union[str, toplevel.String]):
      if name == "Left":
         return "<Button-1>"
      elif name == "Middle":
         return "<Button-2>"
      elif name == "Right":
         return "<Button-3>"
   def tkeventToMouseButtonName(event):
      if event.num == 1:
         return "Left"
      elif event.num == 2:
         return "Middle"
      elif event.num == 3:
         return "Right"
   def tkeventToJavascriptKeycode(event):
      pass
class Darwin:
   def mouseButtonNameToTkname(name:Union[str, toplevel.String]):
      if name == "Left":
         return "<Button-1>"
      elif name == "Middle":
         return "<Button-3>"
      elif name == "Right":
         return "<Button-2>"
   def tkeventToMouseButtonName(event):
      if event.num == 1:
         return "Left"
      elif event.num == 2:
         return "Right"
      elif event.num == 3:
         return "Middle"
   def tkeventToJavascriptKeycode(event):
      pass
 
