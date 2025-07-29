import sys
from . import toplevel as as3

def help():
    return "This module inlcudes many things that might be useful when using this library but aren't in actionscript. EX: a helper for increasing python's maximum recursion depth."

class recursionDepth:
    #used like "with recursionDepth(Number):"
    def __init__(self, limit):
        self.limit = limit
    def __enter__(self):
        self.olimit = sys.getrecursionlimit()
        sys.setrecursionlimit(self.limit)
    def __exit__(self, *args):
        sys.setrecursionlimit(self.olimit)
    @staticmethod
    def set(limit):
        sys.setrecursionlimit(limit)
    @staticmethod
    def get():
        return sys.getrecursionlimit()