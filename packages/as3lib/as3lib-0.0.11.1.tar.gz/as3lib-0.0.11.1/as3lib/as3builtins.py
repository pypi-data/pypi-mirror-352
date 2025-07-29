from importlib import __import__
from . import configmodule

__doc__ = "This module contains the builtin functions and directives from actionscript 3"

def formatToString(obj,objname,*args):
   """
   This function appears in the default implementation of fl.ScrollEvent and many
   others in the fl package but doesn't appear anywhere in the documentation, not
   even in the toplevel section. I'm going to assume that this is a builtin function
   """
   return ''.join(["[",objname] + [f" {i}={getattr(obj, i)}" for i in args] + ["]"])

def as3import(packageName:str,namespace,name:str=None):
   #!Implement * imports
   """
   DO NOT USE THIS YET. I have not decided on the final form this will take as most of it is not implemented yet. The behaviour might change and break things.
   
   Import implementation similar to actionscript. It functions as described below:
   All imports are relative to as3lib
   Will import the object inside of the package with the name of the package (This is currently the best way that I could think of to emulate what actionscript does)
   namespace must be provided as python's globals are global to each module
   
   Arguements:
      packageName - The name and location (with "." as the path separator) of the package. Does not currently support "*" imports
      namespace - The object in which to import the module into. If "*" is provided as the namespace, name is ignored and the package is returned. EX: if an object called obj is provided, the package will be imported as obj.name
      name - The name that the module will be imported as. If name is not provided and the package is not a "*" import, the last part of the packageName is used.
   """
   pkg = packageName.split(".")
   if pkg[-1] == "*":
      raise NotImplemented("\"*\" imports are not implemented yet")
   else:
      file = configmodule.librarydirectory / ("/".join(pkg) + ".py")
      if file.exists():
         if file.is_file():
            with open(file,"rb") as f:
               b = (b := f.read())[:b.find(b"\n")].split(b" ")
            if b[0] == b"#?as3package":
               if len(b) == 1: #Import the object inside of the file that is the same as the file name
                  package = getattr(__import__(f"as3lib.{'.'.join(pkg)}",globals(),locals(),(pkg[-1]),0),pkg[-1])
                  if namespace == "*":
                     return package
                  if isinstance(namespace,dict) and namespace.get("__name__") != None: #Is a globals() dict
                     if name == None:
                        namespace.update({pkg[-1]:package})
                     else:
                        namespace.update({name:package})
                  elif name == None:
                     setattr(namespace,pkg[-1],package)
                  else:
                     setattr(namespace,name,package)
               else: #!When package has specific place to be
                  raise NotImplemented("Packages with specific locations are not implemented.")
         else: #!Is directory
            raise NotImplemented("Importing directories as packages is not implemented yet.")
      else:
         raise Exception(f"Package \"as3lib.{packageName}\" does not exist.")
