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

        self.core = self.parent.parentApp.core
        self.complex_handlers = [
                (self.input_is_navigation_key, self.navigate_to_key)
                ]
        self.add_handlers({
            ord('~'):           self.h_change_to_home,
            ord('`'):           self.h_change_to_home,
            curses.KEY_HOME:    self.h_change_to_home,
            })
        self.change_dir(os.getenv('HOME'))
        return

    def h_change_to_home(self, input):
        home = os.getenv('HOME')
        self.change_dir(home)

    def navigate_to_key(self, input):
        char = chr(input)
        self.core.change_to_key(char)
        self.redraw()
        return

    def change_dir(self, dir):
        self.core.visit_entry( self.core.get_entry( dir ))
        self.redraw()
        return

    def redraw(self):
        self.values = self.core.current_entry.children
        self.parent.set_title_to_cwd()
        self.parent.display()
        return


