import logging
import os
import threading
from pathlib import Path
from typing import Optional, Tuple

import urwid.curses_display
from urwid import Widget

from sodalite.core import History
from sodalite.core.navigate import Navigator
from sodalite.ui import theme, viewmodel
from sodalite.ui.control import NavigateControl, AssignControl, OperateControl, Control
from sodalite.ui.filter import Filter
from sodalite.ui.help import HelpLauncher
from sodalite.ui.hookbox import HookBox
from sodalite.ui.mainpane import MainPane
from sodalite.ui.viewmodel import ViewModel, Topic, Mode
from sodalite.util import env

logger = logging.getLogger(__name__)


class MainFrame(urwid.Frame):  # type: ignore

    def __init__(self, path: Path):
        """

        :param path: the start entry
        """
        history = History.load()
        history.visit(path)
        self.navigator = Navigator(history)
        self.model = ViewModel()
        self.navigator.register(self.model.on_update)
        self.mainpane = MainPane(self.model, self.navigator)
        self.filter = Filter(self.model, self.mainpane.frame)
        super().__init__(self.mainpane)
        self.hookbox = HookBox(self.model, self)

        # setup controllers
        self.control: Control = NavigateControl(self)
        viewmodel.global_mode.register(self.change_controller, topic=Topic.MODE)

    def change_controller(self, mode: Mode) -> None:
        if mode == Mode.NAVIGATE:
            self.control = NavigateControl(self)
        elif mode in viewmodel.ANY_ASSIGN_MODE:
            if type(self.control) is not AssignControl:
                self.control = AssignControl(self)
        elif mode == Mode.OPERATE:
            self.control = OperateControl(self)
        else:
            raise ValueError()

    def keypress(self, size: Tuple[int, int], key: str) -> None:
        with DRAW_LOCK:
            self.control.handle_keypress(size, key)


DRAW_LOCK = threading.RLock()


class MainLoop(urwid.MainLoop):  # type: ignore

    def draw_screen(self) -> None:
        with DRAW_LOCK:
            super(MainLoop, self).draw_screen()


def _create_loop(main: Widget) -> MainLoop:
    return MainLoop(main, palette=theme.palette, handle_mouse=False, pop_ups=True)


MAIN_LOOP = 'MainLoop'
threading.current_thread().setName(MAIN_LOOP)
os.environ['ESCDELAY'] = '0'
frame = None
loop: MainLoop
popupLauncher = None


def run(path: Path) -> None:
    global frame
    global loop
    global popupLauncher
    frame = MainFrame(path)
    popupLauncher = HelpLauncher(frame)
    loop = _create_loop(popupLauncher)
    loop.run()


def resume() -> None:
    loop.stop()
    loop.start()


def exit(cwd: Optional[Path] = None) -> None:
    env.exit_cwd = cwd
    raise urwid.ExitMainLoop()


def redraw_if_external() -> None:
    """
    Redraws the screen if and only if the current thread is NOT the main event loop.
    Use this function in case you need to redraw the screen from outside the main event loop.
    It's safe to call the function from inside the main event loop: nothing will happen.
    :return:
    """
    if not threading.current_thread().getName() == MAIN_LOOP:
        if loop:
            loop.draw_screen()
