import npyscreen
import core
import config as config_module
import actionhook
from mylogger import logger
import theme
import mainform
import os


class App(npyscreen.NPSAppManaged):
    def onStart(self):
        npyscreen.setTheme(theme.Theme)
        self.core = core.Core()
        self.config = config_module.Config()
        self.action_engine = actionhook.ActionEngine( self )
        self.addForm( 'MAIN', mainform.MainForm, name="main")

    def onCleanExit(self):
        self.core.shutdown( )
        _append_to_cwd_pipe( self.core.dir_service.getcwd() )
        logger.info("shutdown")

# before exiting, this needs to be called once;
# or the wrapping script won't stop
# cwd: new working dir after exiting this process
def _append_to_cwd_pipe( cwd ):
    pipe = os.getenv("SODALITE_OUTPUT_PIPE")
    logger.info("pipe is '{}'".format(pipe))
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
        _append_to_cwd_pipe( "." )

