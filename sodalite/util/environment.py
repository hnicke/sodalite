# program will read following environment variables
import logging
import os

ENV_BOOKMARK_DIR = 'BOOKMARK_DIR'
ENV_LOG_FILE = 'LOG_FILE'
ENV_CWD_PIPE = 'CWD_PIPE'
ENV_DB_PATH = 'DB_PATH'
ENV_CONFIG_FILE = 'CONFIG_FILE'

home = os.getenv('HOME')
user_data = os.getenv('XDG_DATA_HOME')
user_config = os.getenv('XDG_CONFIG_HOME')

log_file = os.getenv(ENV_LOG_FILE)
if log_file is None:
    log_file = "/var/log/sodalite.log"

logging.basicConfig(filename=log_file, level=logging.DEBUG,
                    format='%(asctime)s - %(name)-18s - %(levelname)-5s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger('watchdog').setLevel(logging.INFO)

exit_cwd = None

if user_data is None:
    user_data = os.path.join(home, '.local/share/sodalite/')
    if not os.path.exists(user_data):
        os.makedirs(user_data, exist_ok=True)

if user_config is None:
    user_config = os.path.join(home, '.config/sodalite')
    if not os.path.exists(user_config):
        os.makedirs(user_config, exist_ok=True)

db_path = os.getenv(ENV_DB_PATH)
if db_path is None:
    db_path = os.path.join(user_data, 'db.sqlite')
logger.info(f"Using database: {db_path}")

history_path = os.path.join(user_data, 'history')

# might be None
cwd_pipe = os.getenv(ENV_CWD_PIPE)

config_path = os.getenv(ENV_CONFIG_FILE)
if config_path is None:
    config_path = os.path.join(user_config, "sodalite/sodalite.yml")
if not os.path.exists(config_path):
    config_path = "/etc/sodalite.yml"
logger.info(f"Using config file: {config_path}")

bookmark_dir = os.getenv(ENV_BOOKMARK_DIR)
if bookmark_dir is None:
    bookmark_dir = os.path.join(user_data, "bookmarks")
    if not os.path.exists(bookmark_dir):
        os.makedirs(bookmark_dir, exist_ok=True)
