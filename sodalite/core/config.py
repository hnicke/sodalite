import functools
import logging
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import yaml
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from sodalite.core.action_def import ActionName
from sodalite.util import env

logger = logging.getLogger(__name__)


class ConfigNotFound(Exception):
    pass


_ENV_CONFIG_FILE = 'CONFIG_FILE'

CONFIG_TEMPLATE = Path(__file__).parent.absolute() / 'sodalite.conf'


@functools.cache
def _config_file() -> Path:
    env_config_file = os.getenv(_ENV_CONFIG_FILE)
    if env_config_file:
        config_file = Path(env_config_file).absolute()
        if config_file.exists():
            logger.debug(f"Using config file from env variable: '{config_file}'")
            return config_file
    else:
        config_file = Path(env.USER_CONFIG / 'sodalite.conf')
        if config_file.exists():
            logger.debug(f"Using config file '{config_file}'")
            return config_file
        else:
            logger.info(f"Creating config file '{config_file}'")
            shutil.copy(src=CONFIG_TEMPLATE, dst=config_file)
            return config_file

    raise ConfigNotFound()


def _sanitize_keymap(keys: dict['ActionName', str]) -> dict['ActionName', str]:
    # ctrl h equals backspace in terminal emulators
    for action, keybinding in keys.items():
        if keybinding == 'ctrl h':
            keys[action] = 'ctrl h'
    return keys


HooksConfig = dict[str, Optional[dict[str, Union[str, dict[str, str]]]]]


@dataclass
class Configuration:
    hooks: HooksConfig
    keymap: dict['ActionName', str]
    preferred_names: list[str]


@functools.cache
def get() -> Configuration:
    try:
        config_str = _config_file().read_text()
        config_dict = yaml.safe_load(config_str)
        return Configuration(
            hooks=config_dict.get('hooks') or {},
            keymap=_sanitize_keymap({ActionName(x): y for x, y in config_dict.get('keymap') or {}}),
            preferred_names=[x.lower() for x in config_dict.get('preferred_names')] or [],
        )
    except (ParserError, ScannerError):
        logger.exception(f"Failed to parse config file'{_config_file()}': Invalid yaml.", exc_info=True)
        exit(1)
