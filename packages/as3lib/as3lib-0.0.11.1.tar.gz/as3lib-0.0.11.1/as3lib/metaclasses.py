class _AS3_CONSTANTSOBJECT(type):
   """
   Metaclass for objects defining as3 constants.
   Objects with this as a metaclass can:
      - be enumerated
   Objects with this as a metaclass can not:
      - have subclasses
      - have objects inside defined or modified after creation (python has a way around this but please don't)
      - be instantiated properly. You can instantiate these but they will not have any of the functions available to them. This is a weakness of metaclasses and the way python does things.
   """
   def __new__(cls, name, bases, classdict):
      for b in bases:
         if isinstance(b, _AS3_DEFINITIONSOBJECT):
            raise TypeError("type '{0}' is not an acceptable base type".format(b.__name__))
      return type.__new__(cls, name, bases, dict(classdict))
   def __setattr__(cls, name, value):
      print("Error: Can not modify objects inside of a _AS3_CONSTANTSOBJECT object")
   def __delattr__(cls, name):
      print("Error: Can not modify objects inside of a _AS3_CONSTANTSOBJECT object")
   def __iter__(cls):
      for attr in dir(cls):
         if not attr.startswith("__"):
            yield attr
   def hasOwnProperty(cls, name):
      if not name.startswith("__") and name in cls.__dict__:
         return True
      return False
   def isPrototypeOf(cls,name):...
   def propertyIsEnumerable(cls,name):
      return cls.hasOwnProperty(name)
   def setPropertyIsEnumerable(cls,name):
      print("Error: Can not set enumerability of objects inside of a _AS3_CONSTANTSOBJECT. They will always be enumerable.")
   def toLocaleString(cls):
      return cls.toString()
   def toString(cls):
      return {i:cls.__dict__[i] for i in cls.__dict__ if not i.startswith("__")}
   def valueOf(cls):
      return cls
