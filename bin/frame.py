import npyscreen
import core
import config
import actionhook
from mylogger import logger
import navigationpane
import assignpane
import actionpane
import sys
import curses
import theme
import mainform



class Frame(npyscreen.NPSAppManaged):
    def onStart(self):
        npyscreen.setTheme(theme.Theme)
        self.core = core.Core()
        self.config = config.Config()
        self.action_engine = actionhook.ActionEngine( self.config )
        self.addForm("MAIN", mainform.MainForm)

    def onCleanExit(self):
        self.core.shutdown()


if __name__ == "__main__":
    logger.info('starting sodalite')
    app = Frame()
    try:
        app.run()
    except KeyboardInterrupt:
        app.core.shutdown()
        logger.info('bye')

