import os
import threading
import time

import urwid.curses_display

from core.navigator import Navigator
from old_ui.viewmodel import ViewModel
from ui import theme
from ui.filelist import FileList
from ui.hookbox import HookBox


class MainFrame(urwid.Frame):

    def __init__(self):
        self.model = ViewModel(Navigator())
        self.file_list = FileList(self.model)
        super().__init__(self.file_list)
        self.hookbox = HookBox(self.model, self)

    def keypress(self, size, key):
        (maxcol, maxrow) = size
        if self.file_list.frame.focus_part == 'footer':
            return self.file_list.frame.footer.keypress((maxcol,), key)
        if self.file_list.keypress((maxcol,), key):
            return self.hookbox.keypress((maxcol,), key)


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
