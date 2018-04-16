import curses
import logging
import os
import threading
import time

import npyscreen

from ui import theme
from ui.control import MainControl
from ui.entryview import EntrySplitter
from ui.footerbox import NotifyBox, HookBox

logger = logging.getLogger(__name__)


class App(npyscreen.NPSAppManaged):

    def __init__(self):
        super().__init__()

        # disable delay when 'ESC' is pressed
        os.environ['ESCDELAY'] = '0'

    def onStart(self):
        npyscreen.setTheme(theme.Theme)
        self.main = self.addForm('MAIN', MainForm)


class MainForm(npyscreen.FormBaseNew):
    BLANK_LINES_BASE = 0
    BLANK_COLUMNS_RIGHT = 0
    DEFAULT_X_OFFSET = 0
    FIX_MINIMUM_SIZE_WHEN_CREATED = False
    FRAMED = False

    def __init__(self, *args, **keywords):
        self.notify_lock = threading.Lock()
        super().__init__(*args, **keywords)

    def create(self):
        self.min_c = 28
        self.min_l = 10
        self.main_control = MainControl(self)
        self.hookpane = self.add(HookBox, main_control=self.main_control)
        self.notifypane = self.add(NotifyBox)
        self.splitter = self.add(EntrySplitter, main_control=self.main_control)

    def notify(self, message: str, duration: float, attr=curses.A_NORMAL):
        thread = threading.Thread(target=self._notify, args=(message, duration, attr,))
        thread.start()

    def _notify(self, message: str, duration: float, attr: int):
        self.hookpane.display()
        self.notifypane.display()
        self.notify_lock.acquire()
        try:
            logger.info(f"Show notification: '{message}'")
            self.notifypane.notify(message, attr)
            self.notifypane.display()
            time.sleep(duration)
            self.hookpane.display()
        finally:
            self.notify_lock.release()
