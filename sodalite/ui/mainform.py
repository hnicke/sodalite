import curses
import os

import npyscreen

from core.entry import Entry
from core.navigator import Navigator
from ui import commandline, navigationpane, assignpane, actionpane
from ui.viewmodel import ViewModel


class MainForm(npyscreen.FormBaseNew):

    def __init__(self, cycle_widgets=True, *args, **keywords):
        self.navigator: Navigator = None
        self.data = None
        self.in_assign_mode = False
        self.entry_for_assignment = None
        self.navigation_mode_handlers = None
        self.assign_mode_handlers = None
        self.handlers = None
        self.complex_handlers = None
        super(MainForm, self).__init__(cycle_widgets=cycle_widgets, *args, **keywords)

    def draw_form(self):
        max_y, max_x = self.lines, self.columns
        self.curses_pad.hline(0, 0, curses.ACS_HLINE, max_x - 1)
        self.curses_pad.hline(max_y - 2, 0, curses.ACS_HLINE, max_x - 1)

    def create(self):
        self.navigator = self.parentApp.navigator
        self.data = ViewModel(self.navigator.current())
        self.populate()
        self.setup_handlers()
        self.redraw()

    def setup_handlers(self):
        disable_key_handlers = {
            curses.KEY_UP: self.nop,
            curses.KEY_DOWN: self.nop,
            curses.KEY_LEFT: self.nop,
            curses.KEY_RIGHT: self.nop
        }
        common_handlers = {
            "^F": self.navigationpane.h_scroll_page_down,
            "^B": self.navigationpane.h_scroll_page_up,
            "^U": self.navigationpane.h_scroll_half_page_up,
            "^D": self.navigationpane.h_scroll_half_page_down,
        }
        common_handlers.update(disable_key_handlers)
        self.navigation_mode_handlers = {
            "=": self.h_toggle_assign_mode,
            ord('~'): self.h_navigate_to_home,
            ord('`'): self.h_navigate_to_home,
            curses.KEY_HOME: self.h_navigate_to_home,
            ord('.'): self.h_navigate_to_parent,
            "^L": self.h_navigate_forward,
            "^H": self.h_navigate_backward,
            curses.KEY_BACKSPACE: self.h_navigate_backward,
            curses.ascii.DEL: self.h_navigate_backward,
        }
        self.navigation_mode_handlers.update(common_handlers)
        self.assign_mode_handlers = {
            "^N": self.assignpane.h_cursor_line_down,
            "^P": self.assignpane.h_cursor_line_up,
            curses.ascii.NL: self.assignpane.h_choose_selection,
        }
        self.assign_mode_handlers.update(common_handlers)
        self.handlers = self.navigation_mode_handlers
        self.complex_handlers = [
            (self.commandline.t_filter, self.commandline.trigger),
            (self.t_input_is_exit_key, self.h_exit),
            (self.navigationpane.t_input_is_navigation_key, self.h_navigate_to_key),
            (self.assignpane.t_input_is_assign_key, self.assignpane.h_assign_key),
            (self.actionpane.is_action_trigger, self.actionpane.trigger_action)
        ]
        self.statusbar.handlers = {}

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
        entry = self.navigator.visit_child(char)
        self.after_navigation(entry)
        return

    def h_navigate_to_parent(self, input):
        entry = self.navigator.visit_parent()
        self.after_navigation(entry)

    def h_navigate_to_home(self, input):
        home = os.getenv('HOME')
        entry = self.navigator.visit_path(home)
        self.after_navigation(entry)

    def h_navigate_forward(self, input):
        entry = self.navigator.visit_next()
        self.after_navigation(entry)

    def h_navigate_backward(self, input):
        entry = self.navigator.visit_previous()
        self.after_navigation(entry)

    def after_navigation(self, entry: Entry):
        self.data.update(entry)
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
        self.set_title(self.data.current_entry.realpath)

    def set_title(self, title):
        self.statusbar.value = " " + title
        self.statusbar.display()
