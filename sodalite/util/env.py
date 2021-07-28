import functools
import logging.handlers
import os

from pathlib import Path
from typing import Optional

VERSION = '0.19.4'
PROGRAM_NAME = 'sodalite'

# setup logger
_global_logger = logging.getLogger()
_global_logger.setLevel(logging.INFO)
handler = logging.handlers.SysLogHandler(address='/dev/log')
formatter = logging.Formatter(
    f'{PROGRAM_NAME}: %(threadName)-12s - %(name)-18s - %(levelname)-5s - %(message)s')
handler.setFormatter(formatter)
_global_logger.addHandler(handler)
logging.getLogger('sodalite').setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
logger.debug('Starting sodalite')

exit_cwd: Optional[Path] = None
# program will read following environment variables
ENV_DATA_DIR = 'DATA_DIR'
ENV_DB_PATH = 'DB_PATH'

HOME = Path.home()
DATA = Path(os.getenv(ENV_DATA_DIR, f'/usr/share/{PROGRAM_NAME}/')).absolute()
USER_DATA = Path(os.getenv('XDG_DATA_HOME', HOME / '.local/share')).absolute() / PROGRAM_NAME
USER_CONFIG = Path(os.getenv('XDG_CONFIG_HOME', HOME / '.config/')).absolute() / PROGRAM_NAME
ENV_CONFIG_FILE = 'CONFIG_FILE'


@functools.lru_cache
def config_file() -> Path:
    return Path(os.getenv(ENV_CONFIG_FILE, '/etc/sodalite.conf')).absolute()


db_file = Path(os.getenv(ENV_DB_PATH, USER_DATA / 'db.sqlite')).absolute()

buffer = USER_DATA / 'buffer'

dirs = [HOME, DATA, USER_DATA, USER_CONFIG, buffer]
for directory in dirs:
    os.makedirs(directory, exist_ok=True)

logger.debug(f"Using database: {db_file.absolute()}")
