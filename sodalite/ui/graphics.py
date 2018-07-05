import logging
import os
import threading

import urwid.curses_display

from core import dirhistory
from core.navigator import Navigator
from ui import theme
from ui.hookbox import HookBox
from ui.mainpane import MainPane
from ui.viewmodel import ViewModel
from util import environment

logger = logging.getLogger(__name__)


class MainFrame(urwid.Frame):

    def __init__(self, path: str):
        """

        :param path: the start entry
        """
        history = dirhistory.load(path)
        navigator = Navigator(history)
        self.model = ViewModel()
        navigator.register(self.model.on_update)
        self.mainpane = MainPane(self.model, navigator)
        super().__init__(self.mainpane)
        self.hookbox = HookBox(self.model, self)

    def keypress(self, size, key):
        with DRAW_LOCK:
            (maxcol, maxrow) = size
            remaining = maxrow
            remaining -= self.hookbox.rows((maxcol,))
            if self.mainpane.frame.focus_part == 'footer':
                return self.mainpane.frame.footer.keypress((maxcol,), key)
            if self.mainpane.keypress((maxcol, remaining), key):
                return self.hookbox.keypress((maxcol, remaining), key)


DRAW_LOCK = threading.RLock()


class MainLoop(urwid.MainLoop):

    def draw_screen(self):
        with DRAW_LOCK:
            super(MainLoop, self).draw_screen()


def _create_loop(main):
    return MainLoop(main, palette=theme.palette, handle_mouse=False)


MAIN_LOOP = 'MainLoop'
threading.current_thread().setName(MAIN_LOOP)
os.environ['ESCDELAY'] = '0'
frame = None
loop = None


def run(path: str):
    global frame
    global loop
    frame = MainFrame(path)
    loop = _create_loop(frame)
    loop.run()


def resume():
    loop.stop()
    loop.start()


def exit(cwd=None):
    environment.exit_cwd = cwd
    raise urwid.ExitMainLoop()


def redraw_if_external():
    """
    Redraws the screen if and only if the current thread is NOT the main event loop.
    Use this function in case you need to redraw the screen from outside the main event loop.
    It's safe to call the function from inside the main event loop: nothing will happen.
    :return:
    """
    if not threading.current_thread().getName() == MAIN_LOOP:
        if loop:
            loop.draw_screen()
