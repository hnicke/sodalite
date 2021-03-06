import logging.handlers
import os

# setup logger
import tempfile

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

home = os.getenv('HOME')
data = os.getenv(ENV_DATA_DIR, "/usr/share/sodalite/")
user_data = os.getenv('XDG_DATA_HOME', os.path.join(home, ".local/share/sodalite/"))
user_config = os.getenv('XDG_CONFIG_HOME', os.path.join(home, ".config/sodalite/"))
db_file = os.getenv(ENV_DB_PATH, os.path.join(user_data, "db.sqlite"))
history_file = os.path.join(user_data, 'history')

config_file = os.getenv(ENV_CONFIG_FILE, os.path.join(user_config, "sodalite/sodalite.conf"))
if not os.path.exists(config_file):
    config_file = "/etc/sodalite.conf"
if not os.path.exists(config_file):
    config_file = "/usr/share/sodalite/sodalite.conf"

buffer = os.path.join(user_data, "buffer")

dirs = [home, data, user_data, user_config, buffer]
for directory in dirs:
    os.makedirs(directory, exist_ok=True)


logger.debug(f"Using database: {db_file}")
logger.debug(f"Using config file: {config_file}")
