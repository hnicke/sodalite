import npyscreen 
import sys
import os
import entry
import entrypane
from mylogger import logger
import curses
import theme

class NavigationPane(theme.LinePrinter,entrypane.EntryPane,npyscreen.Pager):

    def __init__(self, *args, **keywords):
        npyscreen.Pager.__init__(self, *args, **keywords)
        entrypane.EntryPane.__init__(self)

        self.handlers = {
            }
        return




