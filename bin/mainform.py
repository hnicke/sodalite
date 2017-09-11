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
        # form can be made smaller after creation
        #FIX_MINIMUM_SIZE_WHEN_CREATED = True

    def create(self):
        self.core = self.parentApp.core
        self.populate()
        self.in_assign_mode = False
        self.entry_for_assignment = None
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
            curses.ascii.NL:        self.assignpane.h_choose_selection,
            }
        self.handlers = self.navigation_mode_handlers
        self.complex_handlers = [
                (self.navigationpane.t_input_is_navigation_key, self.h_navigate_to_key),
                (self.assignpane.t_input_is_assign_key, self.assignpane.h_assign_key),
                (self.actionpane.is_action_trigger, self.actionpane.trigger_action)
                ]
        self.change_dir(os.getenv('HOME'))
        self.redraw()
    
    def populate(self):
        middle_x = self.curses_pad.getmaxyx()[1] // 2
        spacing = 1
        self.statusbar = self.add(npyscreen.FixedText, relx=3*spacing, rely=spacing)
        self.statusbar.handlers={}
        self.navigationpane = self.add(navigationpane.NavigationPane, relx=spacing,rely=spacing+1, max_width=middle_x-(2*spacing))
        self.assignpane = self.add(assignpane.AssignPane, relx=spacing, rely=spacing+1, max_width=middle_x-(2*spacing), hidden=True, always_show_cursor=True, editable=False)
        self.actionpane = self.add(actionpane.ActionPane, relx=middle_x+spacing, rely=spacing+1, max_width=middle_x-(3*spacing))

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
            self.assignpane.assign_mode_progress = 'choose-entry'
            self.entry_for_assignment = None


        self.navigationpane.display()
        self.assignpane.display()
        self.redraw()



    def h_navigate_to_key(self, input):
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
        self.actionpane.values = self.parentApp.action_engine.get_actions(self.core.current_entry)
        self.redraw_statusbar()
        self.display()
        return

    def redraw_statusbar(self):
        if self.in_assign_mode:
            if self.assignpane.assign_mode_progress == "choose-entry":
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





