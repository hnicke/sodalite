import npyscreen
import os

from core.navigator import Navigator
from ui import theme, mainform


class App(npyscreen.NPSAppManaged):

    def __init__(self, navigator: Navigator):
        self.navigator = navigator
        super().__init__()

        # disable delay when 'ESC' is pressed
        os.environ['ESCDELAY'] = '0'

    def onStart(self):
        npyscreen.setTheme(theme.Theme)
        self.addForm('MAIN', mainform.MainForm, name="main")
