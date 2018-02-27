import curses
import os

import npyscreen

from core.navigator import Navigator
from ui import theme, mainform


class App(npyscreen.NPSAppManaged):

    def __init__(self, navigator: Navigator, hook_engine):
        self.navigator = navigator
        self.hook_engine = hook_engine
        super().__init__()

        # disable delay when 'ESC' is pressed
        os.environ['ESCDELAY'] = '0'

    def onStart(self):
        npyscreen.setTheme(theme.Theme)
        self.addForm('MAIN', mainform.MainForm, self.navigator, self.hook_engine, name="main")
