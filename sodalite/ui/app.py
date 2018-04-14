import logging
import os

import npyscreen

from ui import theme
from ui.control import MainControl
from ui.entryview import EntrySplitter
from ui.hookpane import HookBox

logger = logging.getLogger(__name__)


class App(npyscreen.NPSAppManaged):

    def __init__(self):
        super().__init__()

        # disable delay when 'ESC' is pressed
        os.environ['ESCDELAY'] = '0'

    def onStart(self):
        npyscreen.setTheme(theme.Theme)
        self.addForm('MAIN', MainForm)


class MainForm(npyscreen.FormBaseNew):
    BLANK_LINES_BASE = 0
    BLANK_COLUMNS_RIGHT = 0
    DEFAULT_X_OFFSET = 0
    FIX_MINIMUM_SIZE_WHEN_CREATED = False
    FRAMED = False

    def __init__(self, *args, **keywords):
        self.splitter = None
        super().__init__(*args, **keywords)

    def create(self):
        values = []
        for x in range(5):
            row = []
            row.append(f'C-{x}')
            row.append(f'hook{x}')
            values.append(row)

        self.main_control = MainControl(self)
        self.hookpane = self.add(HookBox, main_control=self.main_control)
        self.splitter = self.add(EntrySplitter, main_control=self.main_control)

        self.min_c = 28
        self.min_l = 10
