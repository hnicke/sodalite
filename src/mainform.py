import curses
import os

import npyscreen

import actionpane
import assignpane
import commandline
import datamodel
import navigationpane
from mylogger import logger


class MainForm(npyscreen.FormBaseNew):

    def __init__(self, cycle_widgets=True, *args, **keywords):
        super(MainForm, self).__init__(cycle_widgets=cycle_widgets, *args, **keywords)

    def draw_form(self):
        MAXY, MAXX = self.lines, self.columns
        self.curses_pad.hline(0, 0, curses.ACS_HLINE, MAXX - 1)
        self.curses_pad.hline(MAXY - 2, 0, curses.ACS_HLINE, MAXX - 1)

    def create(self):
        self.core = self.parentApp.core
        self.data = datamodel.DataModel(self.core.current_entry.children)
        self.populate()
        self.setup_handlers()

        self.in_assign_mode = False
        self.entry_for_assignment = None
        self.statusbar.handlers = {}
        self.redraw()

    def setup_handlers(self):
        self.disable_key_handlers = {
            curses.KEY_UP: self.nop,
            curses.KEY_DOWN: self.nop,
            curses.KEY_LEFT: self.nop,
            curses.KEY_RIGHT: self.nop
        }
        self.common_handlers = {
            curses.ascii.SP: self.navigationpane.h_scroll_page_down,
            "^B": self.navigationpane.h_scroll_page_up,
            "^U": self.navigationpane.h_scroll_half_page_up,
            "^D": self.navigationpane.h_scroll_half_page_down,
        }
        self.common_handlers.update(self.disable_key_handlers)
        self.navigation_mode_handlers = {
            "=": self.h_toggle_assign_mode,
            ord('~'): self.h_navigate_to_home,
            ord('`'): self.h_navigate_to_home,
            curses.ascii.DEL: self.h_navigate_to_previous,
            curses.KEY_HOME: self.h_navigate_to_home,
        }
        self.navigation_mode_handlers.update(self.common_handlers)
        self.assign_mode_handlers = {
            "^N": self.assignpane.h_cursor_line_down,
            "^P": self.assignpane.h_cursor_line_up,
            curses.ascii.NL: self.assignpane.h_choose_selection,
        }
        self.assign_mode_handlers.update(self.common_handlers)
        self.handlers = self.navigation_mode_handlers
        self.complex_handlers = [
            (self.commandline.t_filter, self.commandline.trigger),
            (self.t_input_is_exit_key, self.h_exit),
            (self.navigationpane.t_input_is_navigation_key, self.h_navigate_to_key),
            (self.assignpane.t_input_is_assign_key, self.assignpane.h_assign_key),
            (self.actionpane.is_action_trigger, self.actionpane.trigger_action)
        ]

    def nop(self, input):
        """
        no operation
        is needed to "disable" keys
        """
        return

    def populate(self):
        MAXY, MAXX = self.lines, self.columns
        middle_x = MAXX // 2
        spacing = 1
        startline = 3
        self.statusbar = self.add(npyscreen.FixedText, relx=3 * spacing, rely=1)
        self.navigationpane = self.add(navigationpane.NavigationPane,
                                       relx=spacing,
                                       rely=startline,
                                       max_width=middle_x - (2 * spacing),
                                       )
        self.assignpane = self.add(assignpane.AssignPane,
                                   relx=spacing,
                                   rely=startline,
                                   max_width=middle_x - (2 * spacing),
                                   hidden=True,
                                   always_show_cursor=True,
                                   editable=False,
                                   )
        self.actionpane = self.add(actionpane.ActionPane,
                                   relx=middle_x + spacing,
                                   rely=startline,
                                   max_width=middle_x - (4 * spacing),
                                   )
        self.commandline = self.add(commandline.Commandline,
                                    relx=spacing,
                                    rely=MAXY - 1,
                                    max_height=1,
                                    begin_entry_at=0,
                                    use_max_space=True,
                                    data=self.data
                                    )

    def t_input_is_exit_key(self, input):
        return input == curses.ascii.ESC or input == curses.ascii.NL

    def h_exit(self, input):
        if self.in_assign_mode:
            self.h_toggle_assign_mode("_")
        else:
            logger.info("call to h_exit")
            self.parentApp.switchForm(None)

    def h_toggle_assign_mode(self, input):
        self.in_assign_mode = not self.in_assign_mode
        self.navigationpane.hidden = self.in_assign_mode
        self.assignpane.hidden = not self.in_assign_mode
        if self.in_assign_mode:
            self.handlers = self.assign_mode_handlers
        else:
            self.handlers = self.navigation_mode_handlers
            self.set_title_to_cwd()
            self.assignpane.assign_mode_progress = 'choose-entry'
            self.entry_for_assignment = None
        self.redraw()

    def h_navigate_to_key(self, input):
        char = chr(input)
        self.core.change_to_key(char)
        self.after_navigation()
        return

    def h_navigate_to_home(self, input):
        home = os.getenv('HOME')
        self.core.change_to_dir(home)
        self.after_navigation()

    def h_navigate_to_previous(self, input):
        self.core.change_to_previous()
        self.after_navigation()

    def after_navigation(self):
        self.data.set_entries(self.core.current_entry.children)
        self.commandline.clear_search("")
        self.redraw()

    def redraw(self):
        self.set_value(self.data.get_filtered_entries())
        self.redraw_statusbar()
        self.display()
        return

    def resize(self):
        super(MainForm, self).resize()
        MAXY, MAXX = self.lines, self.columns
        self.commandline.rely = MAXY - 1

    def redraw_statusbar(self):
        if self.in_assign_mode:
            if self.assignpane.assign_mode_progress == "choose-entry":
                self.set_title("assign key: choose entry")
            else:
                self.set_title("assign key: choose new key")
        else:
            self.set_title_to_cwd()

    def set_title_to_cwd(self):
        self.set_title(self.parentApp.core.current_entry.path)

    def set_title(self, title):
        self.statusbar.value = " " + title
        self.statusbar.display()
