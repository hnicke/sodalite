import logging
import os

logger = logging.getLogger('sodalite')
logger.setLevel(logging.DEBUG)
logfile = os.getenv('LOG_PATH')
if logfile is None:
    logfile = "/var/log/sodalite.log"
fh = logging.FileHandler(logfile)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
