import logging
import os

from ui.app import App
from util import environment

logging.basicConfig(filename=environment.log_file, level=logging.DEBUG,
                    format='%(asctime)s - %(name)-18s - %(levelname)-5s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info('Starting sodalite')
    logger.info(f"Using {environment.config_path} as configuration file")

    app = App()

    try:
        app.run()
        logger.info("Shutting down")
    except KeyboardInterrupt as e:
        logger.info('Received SIGINT')
        exit(1)
    # except _curses.error as e:
    #     logger.error(f"Ncurses error: {e}")
    #     exit(1)
