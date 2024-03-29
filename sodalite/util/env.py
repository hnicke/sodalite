import logging.handlers
import os

from pathlib import Path
from typing import Optional

PROGRAM_NAME = 'sodalite'

# setup logger
_global_logger = logging.getLogger()
_global_logger.setLevel(logging.INFO)
log_socket = Path('/dev/log')
if log_socket.is_socket():
    handler = logging.handlers.SysLogHandler(address='/dev/log')
    formatter = logging.Formatter(
        f'{PROGRAM_NAME}: %(threadName)-10s - %(name)s:%(funcName)s:%(lineno)d - %(levelname)-5s - %(message)s')
    handler.setFormatter(formatter)
    _global_logger.addHandler(handler)
logging.getLogger('sodalite').setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

exit_cwd: Optional[Path] = None
# program will read following environment variables
ENV_DATA_DIR = 'DATA_DIR'
ENV_DB_PATH = 'DB_PATH'

DATA = Path(os.getenv(ENV_DATA_DIR, f'/usr/share/{PROGRAM_NAME}/')).absolute()
USER_DATA = Path(os.getenv('XDG_DATA_HOME', Path.home() / '.local/share')).absolute() / PROGRAM_NAME
USER_CONFIG = Path(os.getenv('XDG_CONFIG_HOME', Path.home() / '.config/')).absolute() / PROGRAM_NAME

db_file = Path(os.getenv(ENV_DB_PATH, USER_DATA / 'db.sqlite')).absolute()

buffer = USER_DATA / 'buffer'

dirs = [USER_DATA, USER_CONFIG, buffer]
for directory in dirs:
    os.makedirs(directory, exist_ok=True)
