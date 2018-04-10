import curses
import logging

import os

import npyscreen
import pyperclip

from core import hook, key
from core.key import Key
from core.navigator import Navigator
from ui import theme
from ui.viewmodel import ViewModel, Mode
from util import environment

logger = logging.getLogger(__name__)


class MainControl:
    def __init__(self, view: 'MyForm'):
        self.view = view
        self.handlers = self.view.handlers
        self.complex_handlers = self.view.complex_handlers

        self.disable_arrow_keys()

    def test_focus(self, input):
        logger.info("got focus on main, yeeah")

    def disable_arrow_keys(self):
        self.view.handlers.update({
            curses.KEY_UP: self.nop,
            curses.KEY_DOWN: self.nop,
            curses.KEY_LEFT: self.nop,
            curses.KEY_RIGHT: self.nop
        })

    def nop(self):
        pass


class EntryControl:
    def __init__(self, view: 'EntryBox', navigator: Navigator, data: ViewModel, main_control: MainControl):
        self.view = view
        self.data = data
        self.navigator = navigator
        self.main_control = main_control

        self.handlers = self.setup_handlers()
        self.complex_handlers = self.setup_complex_handlers()

    def setup_handlers(self):
        return {
            "^F": self.view.multiline.h_scroll_page_down,
            "^B": self.view.multiline.h_scroll_page_up,
            "^U": self.view.multiline.h_scroll_half_page_up,
            "^D": self.view.multiline.h_scroll_half_page_down,
            "6": self.while_waiting,
            ord('.'): self.h_navigate_to_parent,
            "=": self.h_enter_assign_mode,
            ord('~'): self.h_navigate_to_home,
            ord('`'): self.h_navigate_to_home,
            curses.KEY_HOME: self.h_navigate_to_home,
            "^L": self.h_navigate_forward,
            "^H": self.h_navigate_backward,
            curses.KEY_BACKSPACE: self.h_navigate_backward,
            curses.ascii.DEL: self.h_navigate_backward,
            curses.ascii.NL: self.h_exit,
            "^Y": self.copy_to_clipboard
        }

    def while_waiting(self, input):
        npyscreen.setTheme(theme.Theme)
        self.view.update()
        logger.info("waiting")

    def setup_complex_handlers(self):
        return [
            (self.view.filter.t_filter, self.view.filter.trigger),
            (self.is_navigation_key, self.h_navigate_to_key),
            (self.is_action_trigger, self.trigger_hook)
        ]

    def activate(self):
        self.main_control.handlers.update(self.handlers)
        self.main_control.view.complex_handlers = self.complex_handlers
        self.view.parent.hookpane.data = self.data

    def h_navigate_to_key(self, ch):
        self.navigator.visit_child(chr(ch))
        self.view.filter.clear_search("")

    def h_navigate_to_parent(self, ch):
        self.navigator.visit_parent()

    def h_navigate_to_home(self, ch):
        home = os.getenv('HOME')
        self.navigator.visit_path(home)

    def h_navigate_forward(self, ch):
        self.navigator.visit_next()

    def h_navigate_backward(self, ch):
        self.navigator.visit_previous()

    def h_exit(self, ch):
        append_to_cwd_pipe(self.navigator.history.cwd())
        exit(0)

    def t_input_is_exit_key(self, ch):
        isexit = ch == curses.ascii.ESC or ch == curses.ascii.NL
        return isexit

    def is_navigation_key(self, ch):
        try:
            # if self.data.in_assign_mode:
            #     return False
            char = chr(ch)
            return self.navigator.is_navigation_key(char)
        except (ValueError, TypeError):
            return False

    def is_action_trigger(self, ch):
        key = curses.ascii.unctrl(ch)
        return hook.is_hook(key, self.data.current_entry)

    def trigger_hook(self, ch):
        key = curses.ascii.unctrl(ch)
        hook.trigger_hook(key, self.data.current_entry)

    def h_enter_assign_mode(self, input):
        assign_control = AssignControl(self.view, self.data, self.main_control, self.navigator)

    def copy_to_clipboard(self, ch):
        pyperclip.copy(self.data.current_entry.path)


class AssignControl:
    def __init__(self, view: 'EntryBox', data: ViewModel, main_control: MainControl, navigator: Navigator):
        self.navigator = navigator
        self.view = view
        self.data = data
        self.main_control = main_control

        self.old_handlers = self.main_control.view.handlers
        self.old_complex_handlers = self.main_control.view.complex_handlers
        self.chosen_entry = None
        self.main_control.view.complex_handlers = [
            (self.t_input_is_assign_key, self.h_assign_key),
        ]
        self.main_control.view.handlers = {
            "^N": self.h_cursor_line_down,
            "^P": self.h_cursor_line_up,
            curses.ascii.NL: self.h_choose_selection,
            curses.ascii.ESC: self.exit_assign_mode,
            410: self.main_control.view._resize
        }
        self.data.mode = Mode.ASSIGN_CHOOSE_ENTRY
        self.view.multiline.always_show_cursor = True
        self.view.update()

    def t_input_is_assign_key(self, ch):
        try:
            char = chr(ch)
            return char in key.get_all_keys()
        except ValueError:
            return False

    def h_assign_key(self, ch):
        char = chr(ch)
        if self.data.mode == Mode.ASSIGN_CHOOSE_ENTRY:
            match = self.navigator.current_entry.get_child_for_key(Key(char))
            if match is not None:
                self.view.multiline.cursor_line = self.view.values.index(match)
                self.view.multiline.display()
                self.choose_entry(match)
        elif self.data.mode == Mode.ASSIGN_CHOOSE_KEY:
            if self.t_input_is_assign_key(ch):
                char = chr(ch)
                self.navigator.assign_key(Key(char), self.chosen_entry.path)
                self.view.multiline.cursor_line = 0
                self.exit_assign_mode()
        return

    def exit_assign_mode(self, *_):
        self.data.mode = Mode.NORMAL
        self.main_control.view.complex_handlers = self.old_complex_handlers
        self.main_control.view.handlers = self.old_handlers
        self.view.multiline.always_show_cursor = False
        self.data.notify_all()

    def h_choose_selection(self, ch):
        entry = self.view.multiline.values[self.view.multiline.cursor_line]
        self.choose_entry(entry)

    def choose_entry(self, entry):
        if self.data.mode == Mode.ASSIGN_CHOOSE_ENTRY:
            self.chosen_entry = entry
            self.data.mode = Mode.ASSIGN_CHOOSE_KEY
            self.view.update()

    def h_cursor_line_up(self, ch):
        if self.data.mode == Mode.ASSIGN_CHOOSE_ENTRY:
            self.view.multiline.h_cursor_line_up(ch)
            self.view.multiline.display()

    def h_cursor_line_down(self, ch):
        if self.data.mode == Mode.ASSIGN_CHOOSE_ENTRY:
            self.view.multiline.h_cursor_line_down(ch)
            self.view.multiline.display()


class SplitControl:
    def __init__(self, splitter: 'EntrySplitter', main_control: MainControl):
        self.view = splitter
        self.main_control = main_control
        self.main_control.handlers.update({
            curses.KEY_HOME: self.view.h_toggle_split
        })


def append_to_cwd_pipe(cwd: str):
    """Before exiting, this needs to be called once, or the wrapping script won't stop
    :param cwd: a path, will get written to output pipe if pipe exists
    """
    pipe = environment.cwd_pipe
    if pipe is not None and os.path.exists(pipe):
        logger.info("Writing '{}' to cwd_pipe '{}'".format(cwd, environment.cwd_pipe))
        with open(environment.cwd_pipe, 'w') as p:
            p.write(cwd)
            p.close()
