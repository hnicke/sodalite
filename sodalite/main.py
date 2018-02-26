import _curses
import atexit
import logging
import os

from core.config import Config
from core.dirhistory import DirHistory
from core.entryaccess import EntryAccess
from core.entrydao import EntryDao
from core.hook import HookEngine
from core.navigator import Navigator
from ui.app import App
from util import environment

logging.basicConfig(filename=environment.log_file, level=logging.DEBUG,
                    format='%(asctime)s - %(name)-18s - %(levelname)-5s - %(message)s')
logger = logging.getLogger(__name__)


def __append_to_cwd_pipe():
    """Before exiting, this needs to be called once, or the wrapping script won't stop
    :param cwd: a path, will get written to output pipe if pipe exists
    """
    pipe = environment.cwd_pipe
    if pipe is not None and os.path.exists(pipe):
        cwd = history.cwd()
        logger.info("Writing '{}' to cwd_pipe '{}'".format(cwd, environment.cwd_pipe))
        with open(environment.cwd_pipe, 'w') as p:
            p.write(cwd)
            p.close()


if __name__ == "__main__":
    global entry_dao
    global history
    logger.info('Starting sodalite')
    logger.info(f"Using {environment.config_path} as configuration file")

    config = Config()
    hook_engine = HookEngine(config)
    entry_dao = EntryDao()
    access = EntryAccess(entry_dao, hook_engine)
    history = DirHistory()
    navigator = Navigator(history, access)
    app = App(navigator, hook_engine)

    atexit.register(__append_to_cwd_pipe)

    try:
        app.run()
        logger.info("Shutting down")
    except KeyboardInterrupt as e:
        logger.info('Received SIGINT')
        atexit.unregister(__append_to_cwd_pipe)
        exit(1)
    except _curses.error as e:
        logger.error(f"Ncurses error: {e}")
        exit(1)
