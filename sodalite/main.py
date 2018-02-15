import os

import npyscreen

from core import config as config_module, actionhook
from core import navigator
from core.mylogger import logger
from ui import theme, mainform


class App(npyscreen.NPSAppManaged):
    def onStart(self):
        npyscreen.setTheme(theme.Theme)
        self.navigator = navigator.Navigator()
        self.config = config_module.Config()
        self.action_engine = actionhook.ActionEngine(self)
        self.addForm('MAIN', mainform.MainForm, name="main")

    def onCleanExit(self):
        self.navigator.shutdown()
        _append_to_cwd_pipe(self.navigator.dir_service.getcwd())
        logger.info("shutdown")


# before exiting, this needs to be called once;
# or the wrapping script won't stop
# cwd: new working dir after exiting this process
def _append_to_cwd_pipe(cwd):
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
        logger.info('received SIGINT')
        # not writing to cwd_pipe: pipe might be closed already
