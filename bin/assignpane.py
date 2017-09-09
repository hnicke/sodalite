import npyscreen
import entrypane
from enum import Enum
import key
from mylogger import logger
import curses
import theme

class AssignPane(theme.LinePrinter,entrypane.EntryPane,npyscreen.MultiLineAction):


    def __init__(self, *args, **keywords):
        npyscreen.MultiLineAction.__init__(self, *args, **keywords)
        entrypane.EntryPane.__init__(self)

        self.entry_to_change = None
        self.mode = 'choose-entry'
        self.add_handlers({
            "^N":                   self.h_cursor_line_down,
            "^P":                   self.h_cursor_line_up,
            curses.ascii.ESC:       self.h_abort,
            curses.ascii.NL:        self.h_choose_selection,
            })
        self.complex_handlers = [
                (self.input_is_navigation_key, self.assign_key)
                ]
        return


    def h_abort(self, input):
        self.mode = 'choose-entry'
        self.entry_to_change = None
        self.parent.parentApp.switchForm('MAIN')
        self.reset_cursor()
        return

    def h_choose_selection( self, input):
        entry = self.values[self.cursor_line]
        self.choose_entry( entry )


    def choose_entry(self, entry ):
        if self.mode == 'choose-entry':
            self.entry_to_change = entry
            self.mode = 'choose-key'
            self.parent.wStatus1.value = "assign key: choose new key"
            self.parent.wStatus1.display()


    def assign_key(self, input):
        char = chr(input)
        if self.mode == 'choose-entry':
            matches = [ x for x in self.values if x.key.value == char]
            if len(matches) == 1:
                entry = matches[0]
                self.cursor_line = self.values.index(entry)
                self.choose_entry(entry)
            elif len(matches) < 0:
                pass
            else:
                logger.error("While assigning an entry for key change, found '{}'entries for given key '{}'".format(len(matches),char))
        elif self.mode == 'choose-key':
           char = chr(input)
           self.parent.parentApp.core.assign_key ( self.entry_to_change, char )
           self.mode == 'choose-entry'
           self.reset_cursor()
           self.parent.parentApp.switchForm('MAIN')

        return

