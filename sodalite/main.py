import logging

from ui import app
from util import environment

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info('Starting sodalite')

    try:
        app.run()
        if environment.exit_cwd:
            print(environment.exit_cwd)
        logger.info("Shutting down")
    except KeyboardInterrupt as e:
        logger.info('Received SIGINT')
        exit(1)
