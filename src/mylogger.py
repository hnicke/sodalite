import logging
import os


logger = logging.getLogger('sodalite')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler( os.getenv('LOG_FILE'))
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

