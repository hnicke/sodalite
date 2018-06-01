import os
import threading
import time

import urwid.curses_display

from core.navigator import Navigator
from ui import theme
from ui.hookbox import HookBox
from ui.mainpane import MainPane
from ui.viewmodel import ViewModel


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


os.environ['ESCDELAY'] = '0'
frame = MainFrame()
loop = urwid.MainLoop(frame, palette=theme.palette, handle_mouse=False)

notify_box = urwid.LineBox(urwid.Text('', align='center'), tline='')
notify_lock = threading.Lock()
_last_message = ''


def run():
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
