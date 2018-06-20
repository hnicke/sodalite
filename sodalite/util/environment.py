import logging
import os

exit_cwd = None

# program will read following environment variables
ENV_DATA_DIR = 'DATA_DIR'
ENV_BOOKMARK_DIR = 'BOOKMARK_DIR'
ENV_LOG_FILE = 'LOG_FILE'
ENV_DB_PATH = 'DB_PATH'
ENV_CONFIG_FILE = 'CONFIG_FILE'

home = os.getenv('HOME')
data = os.getenv(ENV_DATA_DIR, "/usr/share/sodalite/")
user_data = os.getenv('XDG_DATA_HOME', os.path.join(home, ".local/share/sodalite/"))
bookmark_dir = os.getenv(ENV_BOOKMARK_DIR, os.path.join(user_data, "bookmarks"))
user_config = os.getenv('XDG_CONFIG_HOME', os.path.join(home, ".config/sodalite/"))
log_file = os.getenv(ENV_LOG_FILE, "/var/log/sodalite.log")
db_file = os.getenv(ENV_DB_PATH, os.path.join(user_data, "db.sqlite"))
history_file = os.path.join(user_data, 'history')

config_file = os.getenv(ENV_CONFIG_FILE, os.path.join(user_config, "sodalite/sodalite.conf"))
if not os.path.exists(config_file):
    config_file = "/etc/sodalite.conf"
if not os.path.exists(config_file):
    config_file = "/usr/share/sodalite/sodalite.conf"

dirs = [home, data, user_data, user_config, bookmark_dir]
for directory in dirs:
    os.makedirs(directory, exist_ok=True)

logging.basicConfig(filename=log_file, level=logging.DEBUG,
                    format='%(asctime)s - %(name)-18s - %(levelname)-5s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger('watchdog').setLevel(logging.INFO)

logger.info(f"Using database: {db_file}")
logger.info(f"Using config file: {config_file}")



