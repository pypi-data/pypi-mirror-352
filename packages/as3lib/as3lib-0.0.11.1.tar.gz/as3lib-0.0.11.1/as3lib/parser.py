import os

#Parts of this parser are heavily based on these projects:
#https://github.com/meemknight/C--
#https://github.com/davidcallanan/py-myopl-code

"""
NOTES

look at 
   https://sourceforge.net/projects/osmf.adobe/
   https://sourceforge.net/adobe/smp/home/Strobe%20Media%20Playback/
   https://web.archive.org/web/20140518205828/http://www.osmf.org/
   https://sourceforge.net/adobe/blazeds/wiki/Home/
   https://github.com/adobe-flash/avmplus
   https://github.com/adobe-flash/crossbridge/tree/master
   https://github.com/thibaultimbert/graphicscorelib
   https://github.com/adobe-flash/Webkit4AIR
   https://github.com/adobe/flash-platform
   https://github.com/adobe/GLS3D
   https://github.com/adobe/dds2atf
   https://github.com/adobe/telemetry-utils
   https://github.com/adobe/glsl2agal
   https://github.com/adobe/bin2c
   https://github.com/Corsaair/as3shebang
   https://github.com/mozilla/shumway
   https://github.com/mikechambers/as3corelib
Imports: parse <parent>.<package> and put contained objects (functions/classes/etc) into object with name <package>
Flash built in modules:
   toplevel (autoimported)
   adobe
      utils
   air
      destop
      net
      update
         events
   com
      adobe
         viewsource
   fl
      accessibility
      containers
      controls
         dataGridClasses
         listClasses
         progressBarClasses
      core
      data
      display
      events
      ik
      lang
      livepreview
      managers
      motion
         easing
      rsl
      text
      transitions
         easing
      video
   flash
      accessibility
      concurrent
      crypto
      data
      desktop
      display
      display3D
         textures
      errors
      events
      external
      filesystem
      filters
      geom
      globalization
      html
      media
      net
         dns
         drm
      notifications
      permissions
      printing
      profiler
      sampler
      security
      sensors
      system
      text
         engine
         ime
      ui
      utils
      xml
   flashx
      textLayout
         compose
         container
         conversion
         edit
         elements
         events
         factory
         formats
         operations
         utils
         undo

Flash Movies:
   package <name> {
      import flash.display.MovieClip
      ...other imports...
      public dynamic class <classname> extends MovieClip {
         ...variable definitions...
         public function <classname>() {
            #if I understand correctly, the function with name <classname> is the init, or main, function
            super();
            ...
         }
         ...
      }
   }
"""

__version__ = "dev1"

#Keywords, Statements, and Directives
statements = (
   "break", #breaks out of a loop
   "case", #case in switch-case statement
   "catch", #catch in try-catch-finally statement - handles the errors in the try block
   "continue", #skips to next iteration of a loop
   "default", #default case in switch-case statement
   "do", #do in do-while loop - used like do ({statements}) while (condition) - while loop except all statements in the do block are executed before the condition is checked
   "else", #else statement
   "for", #for loop - can be used as for ([init]; [condition]; [next]){...} or for (variableIterant:String in object){...} or for each (variableIterant in object){...}
   "in", #in in for-in loop
   "while", #while loop
   "each",
   "if", #if statement
   "label", #associates a statement that can be referenced by break or continue
   "return", #returns a value, or null if used by itself
   "super", #invokes the parent version of an object
   "switch", #switch in switch-case statement
   "throw", #throws an error
   "catch", #handles an error
   "try", #try in try-catch-finally statement - trys the code in its block. if an error occurs skip the rest of the block and go to the catch blocks.
   "with",
   "finally" #finally in try-catch-finally - if it exists, always executes after the try and catch portions are done
)
attribute_keywords = (
   "dynamic", #instances of this class may have dynamic properties added at runtime
   "final", #cannot be overrided or extended
   "internal", #only available within a package
   "native", #implemented in binary instead of actionscript
   "override", #replaces inherited method
   "private", #only availably to the class that defines it
   "protected", #only availably to the class that defines it and subclasses of it
   "public", #available to any caller
   "static" #belongs to the class not the instances of it (ex: Math.PI)
)
definition_keywords = (
   "...", #equivalent to *args in python
   "class", #class definition
   "const", #a variable that can be assign a value only once (not including the initial value of Null)
   "extends", #makes a class a subclass of another
   "function", #function definition
   "get", 
   "implements", #specifies that a class implements one or more interfaces
   "interface", #interface definition
   "namespace", #allows visibility contol of definitions
   "package", #organizes code into a group that can be imported
   "set", 
   "var" #variable definition
)
directives = (
   "default xml namespace",
   "import", #imports external code
   "include", #imports code from a file like it was part of the calling file
   "use namespace"
)
namespaces = (
   "AS3",
   "flash_proxy",
   "object_proxy"
)
primary_expression_keywords = (
   "false", #Boolean false
   "null", #special value that represents no value
   "this", #reference to containing object, roughly equivalent to "self" in python
   "true" #Boolean true
)
operator_keywords = (
   "as",
   "delete", #deletes objects
   "in",
   "instanceof",
   "is",
   "new",
   "typeof"
)
keywords = statements + attribute_keywords + definition_keywords + directives + operator_keywords + primary_expression_keywords

T_KEYWORD = "KEYWORD"
T_IDENTIFIER = "IDENTIFIER"
T_SPACE = "SPACE"
T_NEWLINE = "NEWLINE"
T_PARSERFUNCTION = "PARSERFUNCTION"
T_EOF = "EOF"

#Primative Types
TPRIM_ARRAY = "PRIMARRAY"
TPRIM_BOOLEAN = "PRIMBOOLEAN"
TPRIM_NUMBER = "PRIMNUMBER"
TPRIM_STRING = "PRIMSTRING"

#Operators
O_ADD = "ADD" # +
O_DEC = "DEC" # --
O_DIV = "DIV" # /
O_INC = "INC" # ++
O_MOD = "MOD" # %
O_MUL = "MUL" # *
O_SUB = "SUB" # -

O_AADD = "AADD" # +=
O_ADIV = "ADIV" # /=
O_AMOD = "AMOD" # %=
O_AMUL = "AMUL" # */
O_ASUB = "ASUB" # -=

O_ASSIGN = "ASSIGN" # =

O_BAND = "BAND" # &
O_BLSH = "BLSH" # <<
O_BNOT = "BNOT" # ~
O_BOR = "BOR" # |
O_BRSH = "BRSH" # >>
O_BURS = "BURS" # >>>
O_BXOR = "BXOR" # ^

O_BAAND = "BAAND" # &=
O_BALSH = "BALSH" # <<=
O_BAOR = "BAOR" # |=
O_BARSH = "BARSH" # >>=
O_BAURS = "BAURS" # >>>=
O_BAXOR = "BAXOR" # ^=

O_BLCOMM = "BLCOMM" # /*
O_BRCOMM = "BRCOMM" # */
O_LCOMM = "LCOMM" # //

O_COMEQ = "COMEQ" # ==
O_COMGT = "COMGT" # >
O_COMGTE = "COMGTE" # >=
O_COMINQ = "COMINQ" # !=
O_COMLT = "COMLT" # <
O_COMLTE = "COMLTE" # <=
O_COMSEQ = "COMSEQ" # ===
O_COMSINQ = "COMSINQ" # !==

O_LAND = "LAND" # &&
O_LAAND = "LAAND" # &&=
O_LNOT = "LNOT" # !
O_LOR = "LOR" # ||
O_LAOR = "LAOR" # ||=

#O_AS = "AS" # as
O_COMMA = "COMMA" # ,
O_CNDTN = "CNDTN" # ?:
#O_DEL = "DEL" # delete
O_DOT = "DOT" # .
O_2DOT = "2DOT" # ..
O_ELIPSE = "ELIPSE" # ...
#O_IN = "IN" # in
#O_INSTOF = "INSTOF" # instanceof
#O_IS = "IS" # is
O_NMQUAL = "NMQUAL" # ::
#O_NEW = "NEW" # new
O_LSBRAC = "LSBRAC" # [
O_RSBRAC = "RSBRAC" # ]
O_LCBRAC = "LCBRAC" # {
O_RCBRAC = "RCBRAC" # }
O_LPAREN = "LPAREN" # (
O_RPAREN = "RPAREN" # )
O_REGEXP = "REGEXP" # /
O_COLON = "COLON" # :
#O_TYPE = "TYPE" # :
#O_TYPEOF = "TYPEOF" # typeof
O_OPVOID = "OPVOID" # void

O_SCON = "SCON" # +
O_SACON = "SACON" # +=
O_SDELIM = "SDELIM" # "

O_XMLATTR = "XMLATTR" # @
O_XMLLBRCE = "XMLLBRCE" # {
O_XMLRBRCE = "XMLRBRCE" # }
O_XMLLBRCK = "XMLLBRCK" # [
O_XMLRBRCK = "XMLRBRCK" # ]
O_XMLCONC = "XMLCONC" # +
O_XMLACON = "XMLACON" # +=
#O_XMLDEL = "XMLDEL" # delete
O_XMLDCND = "XMLDCND" # ..
O_XMLDOT = "XMLDOT" # .
O_XMLLPAREN = "XMLLPAREN" # (
O_XMLRPARRN = "XMLRPAREN" # )
O_XMLLLIT = "XMLLLIT" # <
O_XMLRLIT = "XMLRLIT" # >

O_SEMICOL = "SEMICOL" # ;
O_SEMINEW = "SEMINEW" # ;\n

#Special Types
ST_STAR = "STAR" # *
ST_VOID = "STVOID" # void
ST_NULL = "STNULL" # Null

Numerals = (None,"0","01","012","0123","01234","012345","0123456","01234567","012345678","0123456789","0123456789Aa","0123456789ABab","0123456789ABCabc","0123456789ABCDabcd","0123456789ABCDEabcde","0123456789ABCDEFabcdef","0123456789ABCDEFGabcdefg","0123456789ABCDEFGHabcdefgh","0123456789ABCDEFGHIabcdefghi","0123456789ABCDEFGHIJabcdefghij","0123456789ABCDEFGHIJKabcdefghijk","0123456789ABCDEFGHIJKLabcdefghijkl","0123456789ABCDEFGHIJKLMabcdefghijklm","0123456789ABCDEFGHIJKLMNabcdefghijklmn","0123456789ABCDEFGHIJKLMNOabcdefghijklmno","0123456789ABCDEFGHIJKLMNOPabcdefghijklmnop","0123456789ABCDEFGHIJKLMNOPQabcdefghijklmnopq","0123456789ABCDEFGHIJKLMNOPQRabcdefghijklmnopqr","0123456789ABCDEFGHIJKLMNOPQRSabcdefghijklmnopqrs","0123456789ABCDEFGHIJKLMNOPQRSTabcdefghijklmnopqrst","0123456789ABCDEFGHIJKLMNOPQRSTUabcdefghijklmnopqrstu","0123456789ABCDEFGHIJKLMNOPQRSTUVabcdefghijklmnopqrstuv","0123456789ABCDEFGHIJKLMNOPQRSTUVWabcdefghijklmnopqrstuvw","0123456789ABCDEFGHIJKLMNOPQRSTUVWXabcdefghijklmnopqrstuvwx","0123456789ABCDEFGHIJKLMNOPQRSTUVWXYabcdefghijklmnopqrstuvwxy","0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
Letters = Numerals[36][10:]

ErrTypeSymbols = {"ADD":"+","DEC":"--","DIV":"/","INC":"++","MOD":"%","MUL":"*","SUB":"-","AADD":"+=","ADIV":"/=","AMOD":"%=","AMUL":"*/","ASUB":"-=","ASSIGN":"=","BAND":"&","BLSH":"<<","BNOT":"~","BOR":"|","BRSH":">>","BURS":">>>","BXOR":"^","BAAND":"&=","BALSH":"<<=","BAOR":"|=","BARSH":">>=","BAURS":">>>=","BAXOR":"^=","BLCOMM":"/*","BRCOMM":"*/","LCOMM":"//","COMEQ":"==","COMGT":">","COMGTE":">=","COMINQ":"!=","COMLT":"<","COMLTE":"<=","COMSEQ":"===","COMSINQ":"!==","LAND":"&&","LAAND":"&&=","LNOT":"!","LOR":"||","LAOR":"||=","COMMA":",","CNDTN":"?:","DOT":".","2DOT":"..","ELIPSE":"...","NMQUAL":"::","LSBRAC":"[","RSBRAC":"]","LCBRAC":"{","RCBRAC":"}","LPAREN":"(","RPAREN":")","REGEXP":"/","COLON":":","OPVOID":"void","XMLATTR":"@","SEMICOL":";","SEMINEW":";\\n","STAR":"*","STVOID":"void","STNULL":"Null"}

def isXMLName(str_:str):
   #currently this is spec compatible with the actual xml specs but unknown if it is the same as the actionscript function.
   whitelist = "-_."
   if (len(str_) == 0) or (str_[0].isalpha() == False and str_[0] != "_") or (str_[:3].lower() == "xml") or (str_.find(" ") != -1):
      return False
   for i in str_:
      if i.isalnum() == True or i in whitelist:
         continue
      return False
   return True

class Error_:
   def __init__(self,errname,errdet,startpos,endpos):
      self.errname = errname
      self.errdet = errdet
      self.startpos = startpos
      self.endpos = endpos
   def toString(self):
      return f"{self.errname}; {self.errdet}\nAt line {self.startpos.line + 1}, index {self.startpos.lineindex}"
class ArgumentError_(Error_):
   def __init__(self,errdet,startpos,endpos):
      super().__init__("Argument Error",errdet,startpos,endpos)
class DefinitionError_(Error_):
   def __init__(self,errdet,startpos,endpos):
      super().__init__("Definition Error",errdet,startpos,endpos)
class Error(Error_):
   def __init__(self,errdet,startpos,endpos):
      super().__init__("Error",errdet,startpos,endpos)
class EvalError_(Error_):
   def __init__(self,errdet,startpos,endpos):
      super().__init__("Eval Error",errdet,startpos,endpos)
class RangeError_(Error_):
   def __init__(self,errdet,startpos,endpos):
      super().__init__("Range Error",errdet,startpos,endpos)
class ReferenceError_(Error_):
   def __init__(self,errdet,startpos,endpos):
      super().__init__("Reference Error",errdet,startpos,endpos)
class SecurityError_(Error_):
   def __init__(self,errdet,startpos,endpos):
      super().__init__("Security Error",errdet,startpos,endpos)
class SyntaxError_(Error_):
   def __init__(self,errdet,startpos,endpos):
      super().__init__("Syntax Error",errdet,startpos,endpos)
class TypeError_(Error_):
   def __init__(self,errdet,startpos,endpos):
      super().__init__("Type Error",errdet,startpos,endpos)
class URIError_(Error_):
   def __init__(self,errdet,startpos,endpos):
      super().__init__("URI Error",errdet,startpos,endpos)
class VerifyError_(Error_):
   def __init__(self,errdet,startpos,endpos):
      super().__init__("Verify Error",errdet,startpos,endpos)
class Position:
   def __init__(self,lineindex:int,line:int,overallindex:int,file,text:str):
      self.lineindex = lineindex
      self.line = line
      self.file = file
      self.text = text
      self.overallindex = overallindex
   def __str__(self):
      return f"index: {self.index}; line: {self.line}"
   def increment(self,char):
      self.lineindex += 1
      self.overallindex += 1
      if char == "\n":
         self.line += 1
         self.lineindex = 0
   def incrementby(self,value:int,chars:list):
      while value > 0:
         self.increment(chars[len(chars)-value])
         value -= 1
   def copy(self):
      return Position(self.lineindex,self.line,self.overallindex,self.file,self.text)
class Token:
   def __init__(self,type_,value=None,startpos=None,endpos=None):
      self.type = type_
      self.value = value
      self.startpos = startpos
      self.endpos = endpos
   def equals(self,type_,value):
      if self.type == type_ and self.value == value:
         return True
      return False
   def __repr__(self):
      if self.value != None:
         return f"{self.type}:{self.value}"
      return f"{self.type}"
class Lexer:
   def __init__(self,data,file):
      self.data = data
      self.file = file
      self.position = Position(0,0,0,file,data)
      self.character = self.__inc()
   def __inc(self):
      if self.position.overallindex < len(self.data):
         return self.data[self.position.overallindex]
      else:
         return None
   def increment(self,num:int=1,chars=None):
      if num > 1:
         self.position.incrementby(num,chars)
      else:
         self.position.increment(self.character)
      self.character = self.__inc()
   def tokenize(self):
      tokens = []
      """
      O_CNDTN = "CNDTN" # ?:
      O_REGEXP = "REGEXP" # /
      """
      #! properly handle " ", "\n", "\t, ".", "_"
      popnext = 0
      nextcheck = []
      tonext = False
      while self.character != None:
         if self.character == ";":
            tokens.append(self.detectsemicolon())
         elif self.character == "\n":
            if as3parserdebug == True:
               tokens.append(Token(T_NEWLINE,startpos=self.position))
            self.increment()
         elif self.character in (" ","\t"):
            #if as3parserdebug == True:
            #   tokens.append(Token(T_SPACE,startpos=self.position))
            #   self.increment()
            #else:
            tokens.append(self.detectspace())
         #elif self.data[self.position.overallindex:self.position.overallindex+8] == "Vector.<":
         #   tokens.append(detectvector())
         elif self.character in Numerals[10]:
            tokens.append(self.detectnumber())
         elif self.character in Letters + "_":
            tokens.append(self.detectidentifier())
         elif self.character == "+":
            tokens.append(self.detectadd())
         elif self.character == "-":
            tokens.append(self.detectsub())
         elif self.character == "%":
            tokens.append(self.detectmod())
         elif self.character == "*":
            tokens.append(self.detectmul())
         elif self.character == "/":
            temptok = self.detectdiv()
            if temptok.type in ("SLCOMM","MLCOMM"):
               self.skipcomment(temptok.type)
            else:
               tokens.append(temptok)
         elif self.character == "<":
            tokens.append(self.detectlt())
         elif self.character == ">":
            tokens.append(self.detectgt())
         elif self.character == "=":
            tokens.append(self.detecteq())
         elif self.character == "&":
            tokens.append(self.detectand())
         elif self.character == "|":
            tokens.append(self.detector())
         elif self.character == "^":
            tokens.append(self.detectxor())
         elif self.character == "~":
            tokens.append(Token(O_BNOT,startpos=self.position))
            self.increment()
         elif self.character == "!":
            tokens.append(self.detectnot())
         elif self.character == "(":
            tokens.append(Token(O_LPAREN,startpos=self.position))
            self.increment()
         elif self.character == ")":
            tokens.append(Token(O_RPAREN,startpos=self.position))
            self.increment()
         elif self.character == "{":
            tokens.append(Token(O_LCBRAC,startpos=self.position))
            self.increment()
         elif self.character == "}":
            tokens.append(Token(O_RCBRAC,startpos=self.position))
            self.increment()
         elif self.character == "[":
            tokens.append(Token(O_LSBRAC,startpos=self.position))
            self.increment()
         elif self.character == "]":
            tokens.append(Token(O_RSBRAC,startpos=self.position))
            self.increment()
         elif self.character == ".":
            tokens.append(self.detectdot())
         elif self.character == ",":
            tokens.append(Token(O_COMMA,startpos=self.position))
            self.increment()
         elif self.character == ":":
            tokens.append(self.detectcolon())
         elif self.character == "@":
            err, tok = self.detectxmlidetifier()
            if err != None:
               return [], err
            else:
               tokens.append(tok)
         elif self.character in ('"',"'"):
            tok, err, dec = self.detectstring(tokens[-1].type)
            if err != None:
               return [], err
            else:
               if dec not in (0,None):
                  nextcheck.append("RSBRAC")
                  popnext += 1
                  tonext = True
                  for i in range(0,dec-1):
                     tokens.pop()
               tokens.append(tok)
         elif self.character == "":
            tokens.append()
         else:
            sp = self.position.copy()
            character = self.character
            self.increment()
            return [], SyntaxError_(f"'{character}'",sp,self.position)
         if tonext == True:
            tonext = False
         else:
            if len(nextcheck) != 0:
               if tokens[-1].type != nextcheck[0]:
                  sp = self.position.copy()
                  character = self.character
                  self.increment()
                  return [], SyntaxError_(f"'Expected {ErrTypeSymbols[nextcheck[0]]}, got {character}'",sp,self.position)
               else:
                  nextcheck.pop(0)
            if popnext != 0:
               tokens.pop()
               popnext -= 1
      tokens.append(Token(T_EOF,startpos=self.position))
      #if as3parserdebug == True:
      #   tokens = self.collapseallspace(tokens)
      return tokens, None
   def detectspace(self):
      sp = self.position.copy()
      while self.character in " \t":
         self.increment()
      return Token(T_SPACE,startpos=sp,endpos=self.position)
   def detectsemicolon(self):
      sp = self.position.copy()
      ttype = O_SEMICOL
      self.increment()
      if self.character == "\n" and as3parserdebug == True:
         ttype = O_SEMINEW
         self.increment()
      return Token(ttype,startpos=sp,endpos=self.position)
   def detectnumber(self):
      #add exponents
      sp = self.position.copy()
      num = ""
      past0 = False
      base = 10
      hasper = False
      while True:
         if self.position.lineindex >= len(self.data):
            break
         if past0 == False and self.character == "0":
            self.increment()
            if self.character == "x":
               base = 16
               past0 = True
               self.increment()
            else:
               num += "0"
         else:
            past0 = True
         if base == 16:
            if self.character in Numerals[16]:
               num += self.character
               self.increment()
            else:
               break
         else:
            if self.character in Numerals[10] or (self.character == "." and hasper == False):
               if self.character == ".":
                  hasper = True
               num += self.character
               self.increment()
            else:
               if num[-1] == "." and self.character == " ":
                  #error expect numerals afer period
                  break
               else:
                  break
      if hasper == True:
         #must be number
         return Token(TPRIM_NUMBER,float(num),sp,self.position)
      else:
         return Token(TPRIM_NUMBER,int(num,base),sp,self.position)
   def detectidentifier(self):
      #! add check to see if identifier is all underscores (not valid)
      iden = ""
      sp = self.position.copy()
      while self.character not in (None,"\n") and self.character in f"{Numerals[36]}_":
         iden += self.character
         self.increment()
      if iden[:3] == "___":
         ttype = T_PARSERFUNCTION
         iden = iden[3:]
      elif iden in keywords:
         ttype = T_KEYWORD
      else:
         ttype = T_IDENTIFIER
      return Token(ttype,iden,sp,self.position)
   def skipcomment(self,type_):
      if type_ == "SLCOMM":
         while self.character not in ("\n",None):
            self.increment()
      elif type_ == "MLCOMM":
         while True:
            if self.character == "*":
               self.increment()
               if self.character == "/":
                  self.increment()
                  break
            self.increment()
   def detectadd(self):
      sp = self.position.copy()
      ttype = O_ADD
      self.increment()
      if self.character == "=":
         ttype = O_AADD
         self.increment()
      elif self.character == "+":
         ttype = O_INC
         self.increment()
      return Token(ttype,startpos=sp,endpos=self.position)
   def detectsub(self):
      sp = self.position.copy()
      ttype = O_SUB
      self.increment()
      if self.character == "=":
         ttype = O_ASUB
         self.increment()
      elif self.character == "-":
         ttype = O_DEC
         self.increment()
      return Token(ttype,startpos=sp,endpos=self.position)
   def detectmod(self):
      sp = self.position.copy()
      ttype = O_MOD
      self.increment()
      if self.character == "=":
         ttype = O_AMOD
         self.increment()
      return Token(ttype,startpos=sp,endpos=self.position)
   def detectmul(self):
      sp = self.position.copy()
      ttype = O_MUL
      self.increment()
      if self.character == "=":
         ttype = O_AMUL
         self.increment()
      return Token(ttype,startpos=sp,endpos=self.position)
   def detectdiv(self):
      sp = self.position.copy()
      ttype = O_DIV
      self.increment()
      if self.character == "=":
         ttype = O_ADIV
         self.increment()
      elif self.character == "/":
         ttype = "SLCOMM"
         self.increment()
      elif self.character == "*":
         ttype = "MLCOMM"
         self.increment()
      return Token(ttype,startpos=sp,endpos=self.position)
   def detectlt(self):
      sp = self.position.copy()
      ttype = O_COMLT
      self.increment()
      if self.character == "=":
         ttype = O_COMLTE
         self.increment()
      elif self.character == "<":
         ttype = O_BLSH
         self.increment()
         if self.character == "=":
            ttype = O_BALSH
            self.increment()
      return Token(ttype,startpos=sp,endpos=self.position)
   def detectgt(self):
      sp = self.position.copy()
      ttype = O_COMGT
      self.increment()
      if self.character == "=":
         ttype = O_COMGTE
         self.increment()
      elif self.character == ">":
         ttype = O_BRSH
         self.increment()
         if self.character == "=":
            ttype = O_BARSH
            self.increment()
         elif self.character == ">":
            ttype = O_BAURS
            self.increment()
      return Token(ttype,startpos=sp,endpos=self.position)
   def detecteq(self):
      sp = self.position.copy()
      ttype = O_ASSIGN
      self.increment()
      if self.character == "=":
         self.increment()
         if self.character == "=":
            ttype = O_COMSEQ
            self.increment()
         else:
            ttype = O_COMEQ
      return Token(ttype,startpos=sp,endpos=self.position)
   def detectand(self):
      sp = self.position.copy()
      ttype = O_BAND
      self.increment()
      if self.character == "&":
         ttype = O_LAND
         self.increment()
         if self.character == "=":
            ttype = O_LAAND
            self.increment()
      elif self.character == "=":
         ttype = O_BAAND
         self.increment()
      return Token(ttype,startpos=sp,endpos=self.position)
   def detector(self):
      sp = self.position.copy()
      ttype = O_BOR
      self.increment()
      if self.character == "|":
         ttype = O_LOR
         self.increment()
         if self.character == "=":
            ttype = O_LAOR
            self.increment()
      elif self.character == "=":
         ttype = O_BAOR
         self.increment()
      return Token(ttype,startpos=sp,endpos=self.position)
   def detectxor(self):
      sp = self.position.copy()
      ttype = O_BXOR
      self.increment()
      if self.character == "=":
         ttype = O_BAXOR
         self.increment()
      return Token(ttype,startpos=sp,endpos=self.position)
   def detectnot(self):
      sp = self.position.copy()
      ttype = O_LNOT
      self.increment()
      if self.character == "=":
         ttype = O_COMINQ
         self.increment()
         if self.character == "=":
            ttype = O_COMSINQ
            self.increment()
      return Token(ttype,startpos=sp,endpos=self.position)
   def detectdot(self):
      sp = self.position.copy()
      ttype = O_DOT
      self.increment()
      if self.character == ".":
         ttype = O_2DOT
         self.increment()
         if self.character == ".":
            ttype = O_ELIPSE
            self.increment()
      return Token(ttype,startpos=sp,endpos=self.position)
   def detectcolon(self):
      sp = self.position.copy()
      ttype = O_COLON
      self.increment()
      if self.character == ":":
         ttype = O_NMQUAL
         self.increment()
      return Token(ttype,startpos=sp,endpos=self.position)
   def extendedASCII(self,code):
      match code.lower():
         case "81" | "8d" | "8f" | "90" | "9d":
            return ""
         case "80":
            return "€"
         case "82":
            return "‚"
         case "83":
            return "ƒ"
         case "84":
            return "„"
         case "85":
            return "…"
         case "86":
            return "†"
         case "87":
            return "‡"
         case "88":
            return "ˆ"
         case "89":
            return "‰"
         case "8a":
            return "Š"
         case "8b":
            return "‹"
         case "8c":
            return "Œ"
         case "8e":
            return "Ž"
         case "91":
            return "‘"
         case "92":
            return "’"
         case "93":
            return "“"
         case "94":
            return "”"
         case "95":
            return "•"
         case "96":
            return "–"
         case "97":
            return "—"
         case "98":
            return "˜"
         case "99":
            return "™"
         case "9a":
            return "š"
         case "9b":
            return "›"
         case "9c":
            return "œ"
         case "9e":
            return "ž"
         case "9f":
            return "Ÿ"
         case "a0": #Non-breaking space
            return " "
         case "a1":
            return "¡"
         case "a2":
            return "¢"
         case "a3":
            return "£"
         case "a4":
            return "¤"
         case "a5":
            return "¥"
         case "a6":
            return "¦"
         case "a7":
            return "§"
         case "a8":
            return "¨"
         case "a9":
            return "©"
         case "aa":
            return "ª"
         case "ab":
            return "«"
         case "ac":
            return "¬"
         case "ad": #Soft hyphen
            return "­"
         case "ae":
            return "®"
         case "af":
            return "¯"
         case "b0":
            return "°"
         case "b1":
            return "±"
         case "b2":
            return "²"
         case "b3":
            return "³"
         case "b4":
            return "´"
         case "b5":
            return "µ"
         case "b6":
            return "¶"
         case "b7":
            return "·"
         case "b8":
            return "¸"
         case "b9":
            return "¹"
         case "ba":
            return "º"
         case "bb":
            return "»"
         case "bc":
            return "¼"
         case "bd":
            return "½"
         case "be":
            return "¾"
         case "bf":
            return "¿"
         case "c0":
            return "À"
         case "c1":
            return "Á"
         case "c2":
            return "Â"
         case "c3":
            return "Ã"
         case "c4":
            return "Ä"
         case "c5":
            return "Å"
         case "c6":
            return "Æ"
         case "c7":
            return "Ç"
         case "c8":
            return "È"
         case "c9":
            return "É"
         case "ca":
            return "Ê"
         case "cb":
            return "Ë"
         case "cc":
            return "Ì"
         case "cd":
            return "Í"
         case "ce":
            return "Î"
         case "cf":
            return "Ï"
         case "d0":
            return "Ð"
         case "d1":
            return "Ñ"
         case "d2":
            return "Ò"
         case "d3":
            return "Ó"
         case "d4":
            return "Ô"
         case "d5":
            return "Õ"
         case "d6":
            return "Ö"
         case "d7":
            return "×"
         case "d8":
            return "Ø"
         case "d9":
            return "Ù"
         case "da":
            return "Ú"
         case "db":
            return "Û"
         case "dc":
            return "Ü"
         case "dd":
            return "Ý"
         case "de":
            return "Þ"
         case "dc":
            return "ß"
         case "e0":
            return "à"
         case "e1":
            return "á"
         case "e2":
            return "â"
         case "e3":
            return "ã"
         case "e4":
            return "ä"
         case "e5":
            return "å"
         case "e6":
            return "æ"
         case "e7":
            return "ç"
         case "e8":
            return "è"
         case "e9":
            return "é"
         case "ea":
            return "ê"
         case "eb":
            return "ë"
         case "ec":
            return "ì"
         case "ed":
            return "í"
         case "ee":
            return "î"
         case "ef":
            return "ï"
         case "f0":
            return "ð"
         case "f1":
            return "ñ"
         case "f2":
            return "ò"
         case "f3":
            return "ó"
         case "f4":
            return "ô"
         case "f5":
            return "õ"
         case "f6":
            return "ö"
         case "f7":
            return "÷"
         case "f8":
            return "ø"
         case "f9":
            return "ù"
         case "fa":
            return "ú"
         case "fb":
            return "û"
         case "fc":
            return "ü"
         case "fd":
            return "ý"
         case "fe":
            return "þ"
         case "ff":
            return "ÿ"
   def detectstring(self,prevttype=None):
      #There is no difference between strings inside ' and " except for how said characters are used within the
      #string. If the string starts with ', to use ' within the string, you must use a backslash before it or
      #use the right/left quote mark instead of the straight one. The same is true with " accept the character
      #that must be escaped is " instead.
      sp = self.position.copy()
      ttype = TPRIM_STRING
      stringtype = self.character
      self.increment()
      stringvalue = ""
      if prevttype == "LSBRAC" and self.character == "@":
         err, tok = self.detectxmlidetifier(True,stringtype)
         return tok, err, 2
      else:
         while True:
            if self.character == stringtype:
               break
            if self.character == "\\":
               self.increment()
               if self.character == "b":
                  stringvalue = stringvalue[:-1]
                  self.increment()
               elif self.character == "f":
                  stringvalue += '\f'
                  self.increment()
               elif self.character == "n":
                  stringvalue += '\n'
                  self.increment()
               elif self.character == "r":
                  #!
                  if crisnl == True:
                     stringvalue += "\n"
                  else:
                     bsnindex = stringvalue.rfind("\n")
                     if bsnindex == -1:
                        stringvalue = ""
                     else:
                        stringvalue = stringvalue[:bsnindex+1]
                  self.increment()
               elif self.character == "t":
                  stringvalue += '\t'
                  self.increment()
               elif self.character == "u":
                  self.increment()
                  code = ""
                  for i in range(0,4):
                     code += self.character
                     self.increment()
                  stringvalue += chr(int(code,16))
               elif self.character == "\\":
                  self.increment()
                  if self.character == "x":
                     self.increment()
                     code = ""
                     for i in range(0,2):
                        code += self.character
                        self.increment()
                     if int(code,16) > 128:
                        stringvalue += self.extendedASCII(code)
                     else:
                        stringvalue += bytes.fromhex(code).decode("ascii")
                  else:
                     stringvalue += "\\"
               elif self.character == "'":
                  stringvalue += "'"
                  self.increment()
               elif self.character == '"':
                  stringvalue += '"'
                  self.increment()
            else:
               stringvalue += self.character
               self.increment()
         self.increment()
         return Token(ttype,stringvalue,sp,self.position), None, 0
   def detectxmlidetifier(self,isstr=False,strtype=None):
      sp = self.position.copy()
      self.increment()
      arrstr = False
      skiploop = False
      valid = True
      tinvalid = 0
      name = ""
      if f"{self.character}{self.data[self.position.overallindex + 1]}" == '["':
         self.increment()
         self.increment()
         arrstr = True
      if self.character == " ":
         valid = False
         tinvalid = 5
         skiploop = True
         self.increment()
      elif self.character == None:
         valid = False
         tinvalid = 3
         skiploop = True
         self.increment()
      elif self.character.isalpha() == False and self.character != "_":
         valid = False
         tinvalid = 1
      while True and not skiploop:
         if len(name) == 3 and name.lower() == "xml":
            valid = False
            tinvalid = 2
         if arrstr == True:
            if self.character == '"':
               self.increment()
               if self.character == "]":
                  self.increment()
                  break
               else:
                  valid = False
                  tinvalid = 4
                  self.increment()
                  break
            if self.character == None:
               valid = False
               tinvalid = 3
               self.increment()
               break
            if self.character == " ":
               valid = False
               tinvalid = 6
               self.increment()
         else:
            if isstr == True and self.character == strtype:
               self.increment()
               break
            if self.character in (" ",None):
               self.increment()
               break
         if self.character.isalnum() == True or self.character in "-_.":
            name += self.character
            self.increment()
      if valid == True:
         return None, Token(O_XMLATTR,name,sp,self.position)
      else:
         match tinvalid:
            case 1:
               return SyntaxError_(f"Xml names must start with a letter or underscore, got name {name}",sp,self.position), None
            case 2:
               return SyntaxError_(f"Xml names can not start with the characters 'xml', got name {name}",sp,self.position), None
            case 3:
               return SyntaxError_(f"'Xml name declarations that start with '@[\"' must end with '\"]''",sp,self.position), None
            case 4:
               return SyntaxError_(f"'Xml names can not contain '\"''",sp,self.position), None
            case 5:
               return SyntaxError_(f"'Xml names can not start with spaces'",sp,self.position), None
            case 6:
               return SyntaxError_(f"'Xml names can not contain with spaces'",sp,self.position), None
            case _:
               return SyntaxError_(f"Invalid Xml name, got name {name}",sp,self.position), None
   def collapseallspace(self,tokens_):
      i = 0
      while True:
         if i < (len(tokens_)-1) and tokens_[i].type == tokens_[i+1].type == "SPACE":
            tokens_[i].endpos = tokens_[i+1].endpos
            tokens_.pop(i+1)
         else:
            i += 1
            if i >= (len(tokens_)-1):
               break
      return tokens_

class ValueNode:
   def __init__(self,token,type_):
      self.token = token
      self.type_ = type_
      self.startpos = self.token.startpos
      self.endpos = self.token.endpos
   def __repr__(self):
      return f'{self.token}'
class ArrayNode:
   def __init__(self,elementnodes,startpos,endpos):
      self.elementnodes = elementnodes
      self.startpos = startpos
      self.endpos = endpos
class VariableAssignNode:
   def __init__(self,varnametoken):
      self.varnametoken = varnametoken
      self.startpos = self.varnametoken.startpos
      self.endpos = self.varnametoken.endpos
class VariableAccessNode:
   def __init__(self,varnametoken,valuenode):
      self.varnametoken = varnametoken
      self.valuenode= valuenode
      self.startpos = self.varnametoken.startpos
      self.endpos = self.valuenode.endpos
class BinaryOperationNode:
   def __init__(self,leftnode,operationtoken,rightnode):
      self.leftnode = leftnode
      self.operationtoken = operationtoken
      self.rightnode = rightnode
      self.startpos = self.leftnode.startpos
      self.endpos = self.rightnode.endpos
   def __repr__(self):
      return f"({self.leftnode}, {self.operationtoken}, {self.rightnode})"
class UnaryOperationNodes:
   def __init__(self,operationtoken,node):
      self.operationtoken = operationtoken
      self.node = node
      if operationtoken in (O_INC,O_DEC):
         if operationtoken.startpos > node.startpos:
            self.place = "POST"
            self.startpos = self.node.startpos
            self.endpos = self.operationtoken.endpos
         else:
            self.place = "PRE"
            self.startpos = self.operationtoken.startpos
            self.endpos = self.node.endpos
      else:
         self.place = None
         self.startpos = self.operationtoken.startpos
         self.endpos = self.node.endpos
   def __repr__(self):
      if self.place != None:
         return f"({self.place}_{self.operationtoken}, {self.node})"
      else:
         return f"({self.operationtoken}, {self.node})"
class ParserResult:
   def __init__(self):
      self.error = None
      self.node = None
      self.lastincrementcount = 0
      self.incrementcount = 0
      self.reversecount = 0
   def increment(self):
      self.lastincrementcount = 1
      self.incrementcount += 1
   def register(self,res):
      self.lastincrementcount = res.incrementcount
      self.incrementcount += res.incrementcount
      if res.err != None:
         self.error = res.error
      return res.node
   def tryregister(self,res):
      if res.error != None:
         self.reversecount = res.incrementcount
         return None
      return self.register(res)
   def success(self,node):
      self.node = node
      return self
   def failure(self,error):
      if not self.error or self.lastincrementcount == 0:
         self.error = error
      return self
class Parser:
   def __init__(self,tokens):
      self.tokens = tokens
      self.index = 0
      self.currenttoken = ""
      self.setcurrenttoken()
   def setcurrenttoken(self):
      if self.index >= 0 and self.index < len(self.tokens):
         self.currenttoken = self.tokens[self.index]
   def increment(self):
      self.index += 1
      self.setcurrenttoken()
      return self.currenttoken
   def decrement(self,value=1):
      self.index -= value
      self.setcurrenttoken()
      return self.currenttoken
   def parse(self):
      pass

class Table:
   def __init__(self,parent=None):
      self.elements = {}
      self.parent = parent
   def __getitem__(self,item):
      value = self.elements[item]
      if value == None and self.parent != None:
         return self.parent.get(name)
      return value
   def __setitem__(self,item,value):
      self.elements[item] = value
   def delete(self,item):
      self.elements.pop(item)

class undefined:
   __slots__ = ("value")
   def __init__(self):
      self.value = None
   def __str__(self):
      return "undefined"
   def __repr__(self):
      return "None"
class null:
   __slots__ = ("value")
   def __init__(self):
      self.value = None
   def __str__(self):
      return "null"
   def __repr__(self):
      return "None"

class Value:
   def __init__(self):
      self.setcontext()
      self.setposition()
   def setcontext(self,context=None):
      self.context = context
      return self
   def setposition(self,startpos=None,endpos=None):
      self.startpos = startpos
      self.endpos = endpos
      return self
   def concat(self,value):
      return null()
   def toBoolean(self):
      return null()
   def toString(self):
      return null()
   def toNumber(self):
      return null()

class Array(Value):
   def __init__(self,elements):
      super().__init__()
      self.elements = elements

class Boolean(Value):
   def __init__(self,value):
      super().__init__()
      self.value = value

class Number(Value):
   def __init__(self,value):
      super().__init__()
      self.value = value

Number.MAX_VALUE = 1.79e308
Number.MIN_VALUE = 5e-324
#Number.NaN = NaN()
#Number.NEGATIVE_INFINITY = NInfinity()
#Number.POSITIVE_INFINITY = Infinity()

class String(Value):
   def __init__(self,value):
      super().__init__()
      self.value = value

"""
int:
   MAX_VALUE = 2147483647 (abs-max)
   MIN_VALUE = -2147483648 (abs-min)
uint:
   MAX_VALUE = 4294967295 (abs-max)
   MIN_VALUE = 0 (abs-min)
Number:
   MAX_VALUE = 1.79769313486231570814527423732E308 ?(abs-max)
   MIN_VALUE = 4.94065645841246544176568792868E-324 ?(closest to zero)
"""


class builtinfunctions:
   pass
Symbols = Table()
Symbols["null"] = None
Symbols["undefined"] = None
Symbols["false"] = False
Symbols["true"] = True
Symbols["**help"] = None
Symbols["**quit"] = None
Symbols["**exit"] = None
Symbols["**file"] = None
Symbols["**debug"] = None
Symbols["*&debug"] = None
Symbols["**crisnl"] = None
Symbols["*&crisnl"] = None
#Symbols["null"] = None
as3parserdebug = False
crisnl = False
def strtobool(str_):
   str_ = str_.lower()
   if str_ == "false":
      return False
   elif str_ == "true":
      return True
def parserdebug(str_):
   global as3parserdebug
   as3parserdebug = strtobool(str_)
def crnl(str_):
   #crisnl - carriage return is new line
   global crisnl
   crisnl = strtobool(str_)
def parse_prompt():
   #Symbols["clear"] = None
   #Symbols["cls"] = None
   print(f"ActionScript 3 parser version {__version__}\nType quit or exit to exit.")
   while True:
      pf = False
      line = input("AS3 > ")
      if line in ("exit","quit"):
         break
      elif line in ("clear","cls"):
         os.system("clear" if os.name != "nt" else "cls")
         continue
      elif line == "help":
         print("Not Implemented")
         continue
      elif line[:7] == "**file ":
         pf = True
      elif line[:8] == "**debug ":
         parserdebug(line[8:])
         continue
      elif line == "*&debug":
         print(as3parserdebug)
         continue
      elif line[:9] == "**crisnl ":
         crnl(line[9:])
         continue
      elif line == "*&crisnl":
         print(crisnl)
         continue
      if pf == True:
         result,error = parse_file(line[7:])
      else:
         result,error = parse(line)
      if error != None:
         print(error.toString())
      elif result != None:
         print(result)

def parse(input_,filepath=None):
   string = input_.strip()
   lexer = Lexer(string,filepath)
   tokens,error = lexer.tokenize()
   if as3parserdebug == True:
      debug_printoutputtofile(tokens,"/run/media/ajdelgaruda/6d231072-36c3-4628-9690-1f13b42eee72/ajdel/Desktop/pimin/dev/pyminlib/as3lib/as3lib/parsed.txt")
   if error != None:
      return None, error
   parser = Parser(tokens)
   parsed = parser.parse()
   return tokens,None

def parse_file(filepath,timed=False):
   filepath = filepath.lstrip()
   with open(filepath,"r") as file:
      filetext = file.read()
   if timed == True:
      import timeit
      from functools import partial
      print(timeit.timeit(partial(parse,filetext,filepath),number=1))
   else:
      result,error = parse(filetext,filepath)
      if error != None:
         print(error.toString())
      elif result != None:
         print(result)
      return result,error

def debug_prepareoutput(output):
   return f"{output}"[1:][:-1].replace(", NEWLINE, ", "\n")
def debug_printoutputtofile(output,file):
   with open(file,"w") as f:
      f.write(debug_prepareoutput(output))

class templist(list):
   def indexOf(self,value):
      try:
         return self.index(value)
      except:
         return -1
if __name__ == "__main__":
   import sys
   print("Warning: This parser is nowhere near complete yet. There is still a lot to do.")
   execargs = templist(sys.argv)
   if execargs.indexOf("-d") != -1 or execargs.indexOf("--debug") != -1:
      as3parserdebug = True
   if execargs.indexOf("-cn") != -1 or execargs.indexOf("--crisnl") != -1:
      crisnl = True
   if len(execargs) == 1:
      parse_prompt()
   elif execargs.indexOf("-h") != -1 or execargs.indexOf("--help") != -1:
      print("Usage:\npython parser.py [option] ... [arg]\n\nOptions:\n  -cn,  --crisnl     : makes carriage return (\\r) behave like newline (\\n)\n   -h,  --help       : shows this message\n   -d,  --debug      : enables as3 debug mode\n   -t,  --time       : displays time it took to parse on completion,\n                       does not display parser output\n\nArguements:\n   -f filepath       : file to parse\n   --file\n   -p, --parser      : (default) opens single line parser")
   else:
      if execargs.indexOf("-f") != -1 or execargs.indexOf("--file") != -1:
         timed = False
         if execargs.indexOf("-t") != -1 or execargs.indexOf("--time") != -1:
            timed = True
         ft1 = execargs.indexOf("-f")
         ft2 = execargs.indexOf("--file")
         if ft1 > ft2:
            argnum = ft1 + 1
         else:
            argnum = ft2 + 1
         parse_file(execargs[argnum],timed)
      elif execargs.indexOf("-p") != -1 or execargs.indexOf("--parser") != -1:
         parse_prompt()
      else:
         parse_prompt()
"""
Usage:
python parser.py [option] ... [arg]

Options:
  -cn,  --crisnl     : makes carriage return (\\r) behave like newline (\\n)
   -h,  --help       : shows this message
   -d,  --debug      : enables as3 debug mode
   -t,  --time       : displays time it took to parse on completion,
                       does not display parser output

Arguements:
   -f filepath       : file to parse
   --file
   -p, --parser      : (default) opens single line parser
"""
