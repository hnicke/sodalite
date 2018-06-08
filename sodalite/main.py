import logging

from ui import app

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info('Starting sodalite')

    try:
        app.run()
        logger.info("Shutting down")
    except KeyboardInterrupt as e:
        logger.info('Received SIGINT')
        exit(1)
