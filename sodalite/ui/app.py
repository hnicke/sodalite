import logging
import os
import threading
import time

import urwid.curses_display

from core.navigator import Navigator
from ui import theme
from ui.hookbox import HookBox
from ui.mainpane import MainPane
from ui.viewmodel import ViewModel

logger = logging.getLogger(__name__)


class MainFrame(urwid.Frame):

    def __init__(self):
        self.model = ViewModel(Navigator())
        self.mainpane = MainPane(self.model)
        super().__init__(self.mainpane)
        self.hookbox = HookBox(self.model, self)

    def keypress(self, size, key):
        (maxcol, maxrow) = size
        remaining = maxrow
        remaining -= self.hookbox.rows((maxcol,))
        if self.mainpane.frame.focus_part == 'footer':
            return self.mainpane.frame.footer.keypress((maxcol,), key)
        if self.mainpane.keypress((maxcol, remaining), key):
            return self.hookbox.keypress((maxcol, remaining), key)


def _create_loop(main):
    return urwid.MainLoop(main, palette=theme.palette, handle_mouse=False)


MAIN_LOOP = 'MainLoop'
threading.current_thread().setName(MAIN_LOOP)
os.environ['ESCDELAY'] = '0'
frame = None
loop = None

notify_box = urwid.LineBox(urwid.Text('', align='center'), tline='')
notify_lock = threading.Lock()
_last_message = ''


def run():
    global frame
    global loop
    frame = MainFrame()
    loop = _create_loop(frame)
    loop.run()


def notify(message, duration=1.5):
    thread = threading.Thread(target=_notify, args=(message, duration,))
    thread.daemon = True
    thread.start()


def _notify(message, duration):
    global _last_message
    if notify_lock.locked() and _last_message == message:
        return
    notify_lock.acquire()
    original_footer = frame.footer
    frame.footer = notify_box
    notify_box.base_widget.set_text(message)
    loop.draw_screen()
    _last_message = message
    time.sleep(duration)
    frame.footer = original_footer
    notify_lock.release()
    loop.draw_screen()


def resume():
    global loop
    # this is a hack. could not figure out how to redraw/refresh the old screen
    # (during pause, app might have missed resizing events)
    # so crudely use new loop
    loop = _create_loop(frame)
    loop.run()


def exit():
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
