import npyscreen
import core
import config
import actionhook
from mylogger import logger
import theme
import mainform
import os


class App(npyscreen.NPSApp):
    def main(self):
        npyscreen.setTheme(theme.Theme)
        self.core = core.Core()
        self.config = config.Config()
        self.action_engine = actionhook.ActionEngine( self.config, self.core )
        F = mainform.MainForm ( self )
        #F.wStatus2.value = "Second Status Line "
        F.edit()

    def onCleanExit(self):
        self.core.shutdown( 0, self.core.dir_service.getcwd() )

def _append_to_cwd_pipe( cwd ):
    pipe = os.getenv("SODALITE_OUTPUT_PIPE")
    with open(pipe, 'w') as p:
        p.write(cwd)
        p.close()

if __name__ == "__main__":
    logger.info('starting sodalite')
    app = App()
    try:
        app.run()
    except KeyboardInterrupt:
        logger.info('got interrupted')
        app.core.shutdown( 1, "." )

