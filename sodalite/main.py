import _curses

import os

import environment
from core.actionhook import ActionEngine
from core.config import Config
from core.navigator import Navigator
from core.dbaccess import DbAccess
from core.dirhistory import DirHistory
from core.entryaccess import EntryAccess
from mylogger import logger
from ui.app import App


def __append_to_cwd_pipe(cwd):
    """Before exiting, this needs to be called once, or the wrapping script won't stop
    :param cwd: a path, will get written to output pipe
    """
    pipe = environment.cwd_pipe
    if pipe is not None and os.path.exists(pipe):
        logger.info("Writing '{}' to cwd_pipe '{}'".format(cwd, environment.cwd_pipe))
        with open(environment.cwd_pipe, 'w') as p:
            p.write(cwd)
            p.close()
    else:
        logger.info("musch")


def clean_exit():
    db_access.close()
    __append_to_cwd_pipe(history.cwd())
    exit(0)


if __name__ == "__main__":
    global db_access
    global history
    logger.info('Starting sodalite')

    db_access = DbAccess()
    access = EntryAccess(db_access)
    history = DirHistory()
    navigator = Navigator(history, access)
    app = App(navigator)
    config = Config()
    action_engine = ActionEngine(config)

    try:
        app.run()
        clean_exit()
        logger.info("Shutting down")
    except KeyboardInterrupt:
        db_access.close()
        logger.info('Received SIGINT')
        # not writing to cwd_pipe: pipe might be closed already
        exit(1)
    except _curses.error:
        # pycharm not stopping program correctly
        # TODO cleanup terminal
        exit(1)
    finally:
        db_access.close()
