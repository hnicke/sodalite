# defines the entry class which represents a file or directiory
import key
import os
if os.name == 'nt':
    import win32api, win32con
from mylogger import logger
from binaryornot.check import is_binary

class Entry:


    def __init__( self, name, parent ):
        self.name = name
        self.parent = parent
        # type has following valid values: file, dir
        self.type = "unknown"
        self.key = key.Key("")
        self.frequency = 0
        # the children of this
        self.children = []

    def get_absolute_path( self ):
        divider = '/'
        if self.parent == '/':
            divider = ''
        return "{}{}{}".format(self.parent, divider, self.name)

    def __str__( self ):
        return "[parent:{}, name:{}, key:{}, type:{}, frequency:{}]".format( self.parent, self.name, self.key, self.type, self.frequency)

    def __repr__(self):
        return str(self)

    def __key( self ):
        return ( self.name, self.parent )

    def __eq__( self, other ):
        return ( type(self) == type(other) and self.__key() == other.__key() )

    def __hash__( self ):
        return (hash(self.__key()))

    def is_hidden(self):
        if os.name == "nt":
            # TODO implement hidden file detection for windows
            raise Exception('Hidden file detection not implemented for windows')
        else:
            return self.name.startswith('.')

    def is_file(self):
        return self.type == 'file'
    
    def is_plain_text_file(self):
        return self.is_file() and not is_binary(self.get_absolute_path())

def sort(entries):
    entries.sort(key=lambda x: x.name)
    entries.sort(key=lambda x: x.type=='dir',reverse=True)
    entries.sort(key=lambda x: x.is_hidden())
    entries.sort(key=lambda x: x.key.value=="")
    entries.sort(key=lambda x: x.frequency,reverse=True)

