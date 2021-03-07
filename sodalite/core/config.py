import logging
import os
import sys
from pathlib import Path

import yaml
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from sodalite.util import env

logger = logging.getLogger(__name__)

config_file = Path(os.getenv('CONFIG_FILE', env.USER_CONFIG / 'sodalite.conf')).absolute()
if not config_file.exists():
    config_file = Path('/etc/sodalite.conf')
    if not config_file.exists():
        config_file = Path('/usr/share/sodalite/sodalite.conf')
logger.debug(f"Using config file: {config_file.absolute()}")


class InvalidConfiguration(Exception):
    pass


def _sanitize_keymap(keys: dict[str, str]) -> dict[str, str]:
    # ctrl h equals backspace in terminal emulators
    for action, keybinding in keys.items():
        if keybinding == 'ctrl h':
            keys[action] = 'ctrl h'
    return keys


try:
    config_str = config_file.read_text()
    config_dict = yaml.safe_load(config_str)
    hooks = config_dict.setdefault('hooks', {})
    if not hooks:
        hooks = {}
    keymap = config_dict.setdefault('keymap', {})
    if not keymap:
        keymap = {}
    keymap = _sanitize_keymap(keymap)
    preferred_names = config_dict.setdefault('preferred_names', [])
    preferred_names = [x.lower() for x in preferred_names]
except ScannerError:
    message = f"Error while parsing config file '{config_file}'"
    print(message, file=sys.stderr)
    logger.exception(message)
    exit(1)
except ParserError:
    message = f"Invalid configuration file '{config_file}': Faulty syntax."
    print(message, file=sys.stderr)
    logger.exception(message)
    exit(1)
