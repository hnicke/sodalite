import npyscreen
from mylogger import logger
import navigationpane
import assignpane
import actionpane
import curses
import os
import key
import sys

class MainForm(npyscreen.FormBaseNew):
    def create(self):
        self.in_assign_mode = False
        # valid values: 'choose-entry' and 'choose-key'
        self.assign_mode_progress = 'choose-entry'
        self.entry_for_assignment = None
        middle_x = self.curses_pad.getmaxyx()[1] // 2
        logger.info(self.curses_pad.getmaxyx())
        spacing = 1
        self.statusbar = self.add(npyscreen.FixedText, relx=3*spacing, rely=spacing)
        self.statusbar.handlers={}
        self.navigationpane = self.add(navigationpane.NavigationPane, relx=spacing,rely=spacing+1, max_width=middle_x-(2*spacing))
        self.assignpane = self.add(assignpane.AssignPane, relx=spacing, rely=spacing+1, max_width=middle_x-(2*spacing), hidden=True)
        #self.curses_pad.vline(0, middle_x, "n", middle_x)
        self.actionpane = self.add(actionpane.ActionPane, relx=middle_x+spacing, rely=spacing+1, max_width=middle_x-(3*spacing))
        self.navigation_mode_handlers = {
                "=":                    self.h_toggle_assign_mode,
                curses.ascii.ESC:       self.h_exit, 
                ord('~'):               self.h_change_to_home,
                ord('`'):               self.h_change_to_home,
                curses.KEY_HOME:        self.h_change_to_home,
                }
        self.assign_mode_handlers = {
            curses.ascii.ESC:       self.h_exit, 
            "^N":                   self.assignpane.h_cursor_line_down,
            "^P":                   self.assignpane.h_cursor_line_up,
            curses.ascii.NL:        self.h_choose_selection,
            }
        self.handlers = self.navigation_mode_handlers
        self.core = self.parentApp.core
        self.complex_handlers = [
                (self.t_input_is_navigation_key, self.h_react_to_key)
                ]
        self.change_dir(os.getenv('HOME'))
        self.redraw()

    def h_change_to_home(self, input):
        home = os.getenv('HOME')
        self.change_dir(home)

    def h_exit(self, input):
        if self.in_assign_mode:
            self.h_toggle_assign_mode("_")
        else:
            sys.exit(0)

    def h_toggle_assign_mode(self, input):
        self.in_assign_mode = not self.in_assign_mode
        self.navigationpane.hidden = self.in_assign_mode
        self.assignpane.hidden = not self.in_assign_mode
        self.display()
        if self.in_assign_mode:
            self.handlers = self.assign_mode_handlers
        else:
            self.handlers = self.navigation_mode_handlers
            self.set_title_to_cwd()
            self.assign_mode_progress = 'choose-entry'
            self.entry_for_assignment = None


        self.navigationpane.display()
        self.assignpane.display()
        self.redraw()

    def t_input_is_navigation_key(self, input):
        char = chr(input)
        is_navigation_key = (char in key.get_all_keys() or char == '.')
        return is_navigation_key

    def h_react_to_key(self, input):
        if self.in_assign_mode:
            self.assign_key(input)
        else:
            self.navigate_to_key(input)

    def assign_key(self, input):
        char = chr(input)
        if self.assign_mode_progress == 'choose-entry':
            matches = [ x for x in self.values if x.key.value == char]
            if len(matches) == 1:
                entry = matches[0]
                self.cursor_line = self.values.index(entry)
                self.choose_entry(entry)
            elif len(matches) < 0:
                pass
            else:
                logger.error("While assigning an entry for key change, found '{}'entries for given key '{}'".format(len(matches),char))
        elif self.assign_mode_progress == 'choose-key':
           char = chr(input)
           self.parentApp.core.assign_key ( self.entry_for_assignment, char )
           self.assign_mode_progress == 'choose-entry'
           #self.reset_cursor()
           self.h_toggle_assign_mode("_")
        return

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
        self.navigationpane.values = self.values
        self.assignpane.values = self.values
        #self.actionpane.values = self.values
        self.redraw_statusbar()
        self.display()
        return

    def redraw_statusbar(self):
        if self.in_assign_mode:
            if self.assign_mode_progress == "choose-entry":
                self.set_title("assign key: choose entry")
            else:
                self.set_title("assign key: choose new key")
        else:
            self.set_title_to_cwd()

    def set_title_to_cwd(self):
        self.set_title(self.parentApp.core.current_entry.get_absolute_path())

    def set_title(self, title):
        self.statusbar.value = " " + title 
        self.statusbar.display()

    def h_choose_selection( self, input):
        entry = self.assignpane.values[self.assignpane.cursor_line]
        self.choose_entry( entry )


    def choose_entry(self, entry ):
        if self.assign_mode_progress == 'choose-entry':
            self.entry_for_assignment = entry
            self.assign_mode_progress = 'choose-key'
            self.redraw_statusbar()




