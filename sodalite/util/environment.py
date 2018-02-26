# program will read following environment variables
import logging
import os

logger = logging.getLogger(__name__)

ENV_BOOKMARK_DIR = 'BOOKMARK_DIR'
ENV_LOG_FILE = 'LOG_FILE'
ENV_CWD_PIPE = 'CWD_PIPE'
ENV_DB_PATH = 'DB_PATH'
ENV_CONFIG_FILE = 'CONFIG_FILE'

home = os.getenv('HOME')
user_data = os.getenv('XDG_DATA_HOME')
user_config = os.getenv('XDG_CONFIG_HOME')

if user_data is None:
    user_data = os.path.join(home, '.local/share/sodalite/')
    if not os.path.exists(user_data):
        os.mkdir(user_data)

if user_config is None:
    user_config = os.path.join(home, '.config/sodalite')
    if not os.path.exists(user_config):
        os.mkdir(user_config)


db_path = os.getenv(ENV_DB_PATH)
if db_path is None:
    db_path = os.path.join(user_data, 'db.sqlite')

# might be None
cwd_pipe = os.getenv(ENV_CWD_PIPE)

log_file = os.getenv(ENV_LOG_FILE)
if log_file is None:
    log_file = "/var/log/sodalite.log"

config_path = os.getenv(ENV_CONFIG_FILE)
if config_path is None:
    config_path = os.path.join(user_config, "sodalite/sodalite.yml")
if not os.path.exists(config_path):
    config_path = "/etc/sodalite.yml"

bookmark_dir = os.getenv(ENV_BOOKMARK_DIR)
if bookmark_dir is None:
    bookmark_dir = os.path.join(user_data, "bookmarks")
    if not os.path.exists(bookmark_dir):
        os.mkdir(bookmark_dir)
