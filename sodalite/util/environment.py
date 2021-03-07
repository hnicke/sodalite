import logging.handlers
import os

from pathlib import Path

# setup logger
_global_logger = logging.getLogger()
_global_logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address='/dev/log')
formatter = logging.Formatter('sodalite: %(name)-18s - %(levelname)-5s - %(message)s')
handler.setFormatter(formatter)
_global_logger.addHandler(handler)
logging.getLogger('watchdog').setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.debug('Starting sodalite')

exit_cwd = None
# program will read following environment variables
ENV_DATA_DIR = 'DATA_DIR'
ENV_DB_PATH = 'DB_PATH'
ENV_CONFIG_FILE = 'CONFIG_FILE'

home = Path(os.environ['HOME'])
data = Path(os.getenv(ENV_DATA_DIR, '/usr/share/sodalite/')).absolute()
user_data = Path(os.getenv('XDG_DATA_HOME', home / '.local/share/sodalite/')).absolute()
history_file = user_data / 'history'
user_config = Path(os.getenv('XDG_CONFIG_HOME', home / '.config/sodalite/')).absolute()
db_file = Path(os.getenv(ENV_DB_PATH, user_data / 'db.sqlite')).absolute()

config_file = Path(os.getenv(ENV_CONFIG_FILE, user_config / 'sodalite/sodalite.conf')).absolute()
if not config_file.exists():
    config_file = Path('/etc/sodalite.conf')
    if not config_file.exists():
        config_file = Path('/usr/share/sodalite/sodalite.conf')

buffer = user_data / 'buffer'

dirs = [home, data, user_data, user_config, buffer]
for directory in dirs:
    os.makedirs(directory, exist_ok=True)

logger.debug(f"Using database: {db_file.absolute()}")
logger.debug(f"Using config file: {config_file.absolute()}")
