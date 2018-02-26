import curses
import os

from core.hook import HookEngine
from core.navigator import Navigator
from ui.assignpane import AssignState
from ui.viewmodel import ViewModel


class Controller:
    def __init__(self, view: 'MainForm', data: ViewModel, navigator: Navigator, hook_engine: HookEngine):
        self.view = view
        self.data = data
        self.navigator = navigator
        self.hook_engine = hook_engine
        self.setup_handlers()

    def nop(self, input):
        """
        no operation
        is needed to "disable" keys
        """
        return

    def setup_handlers(self):
        disable_key_handlers = {
            curses.KEY_UP: self.nop,
            curses.KEY_DOWN: self.nop,
            curses.KEY_LEFT: self.nop,
            curses.KEY_RIGHT: self.nop
        }
        common_handlers = {
            "^F": self.view.navigationpane.h_scroll_page_down,
            "^B": self.view.navigationpane.h_scroll_page_up,
            "^U": self.view.navigationpane.h_scroll_half_page_up,
            "^D": self.view.navigationpane.h_scroll_half_page_down,
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
            "^N": self.view.assignpane.h_cursor_line_down,
            "^P": self.view.assignpane.h_cursor_line_up,
            curses.ascii.NL: self.view.assignpane.h_choose_selection,
        }
        self.assign_mode_handlers.update(common_handlers)
        self.view.handlers = self.navigation_mode_handlers
        self.view.complex_handlers = [
            (self.view.commandline.t_filter, self.view.commandline.trigger),
            (self.t_input_is_exit_key, self.h_exit),
            (self.is_navigation_key, self.h_navigate_to_key),
            (self.view.assignpane.t_input_is_assign_key, self.view.assignpane.h_assign_key),
            (self.view.actionpane.is_action_trigger, self.view.actionpane.trigger_hook)
        ]
        self.view.statusbar.handlers = {}

    def t_input_is_exit_key(self, input):
        return input == curses.ascii.ESC or input == curses.ascii.NL

    def is_navigation_key(self, input):
        try:
            if self.data.in_assign_mode:
                return False
            char = chr(input)
            return self.navigator.is_navigation_key(char)
        except (ValueError, TypeError):
            return False

    def h_navigate_to_key(self, input):
        self.navigator.visit_child(chr(input))
        self.view.commandline.clear_search("")

    def h_navigate_to_parent(self, input):
        self.navigator.visit_parent()

    def h_navigate_to_home(self, input):
        home = os.getenv('HOME')
        self.navigator.visit_path(home)

    def h_navigate_forward(self, input):
        self.navigator.visit_next()

    def h_navigate_backward(self, input):
        self.navigator.visit_previous()

    def h_exit(self, input):
        if self.data.in_assign_mode:
            self.h_toggle_assign_mode("_")
        else:
            self.view.parentApp.switchForm(None)

    def h_toggle_assign_mode(self, input):
        self.data.in_assign_mode = not self.data.in_assign_mode
        self.view.navigationpane.hidden = self.data.in_assign_mode
        self.view.assignpane.hidden = not self.data.in_assign_mode
        if self.data.in_assign_mode:
            self.view.handlers = self.assign_mode_handlers
        else:
            self.view.handlers = self.navigation_mode_handlers
            self.view.set_title_to_cwd()
            self.view.assignpane.state = AssignState.CHOOSE_ENTRY
            self.entry_for_assignment = None
        self.view.update()
