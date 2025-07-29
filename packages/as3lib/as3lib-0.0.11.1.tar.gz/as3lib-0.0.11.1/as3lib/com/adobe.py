import as3lib.flash.ui as fui
import webbrowser
class ViewSource:
   def addMenuItem(obj:object, url:str):
      """
      Adds a "View Source" context menu item to the context menu of the given object.
      Parameters:
         obj:object — The object to attach the context menu item to.
         url:str — The URL of the source viewer that the "View Source" item should open in the browser.
      """
      obj.addItemAt(fui.ContextMenuItem("root","View Source","ViewSource",command=lambda: webbrowser.open(url=url)))
