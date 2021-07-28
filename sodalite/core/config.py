import functools
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import yaml
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from sodalite.util import env

logger = logging.getLogger(__name__)


class ConfigNotFound(Exception):
    pass


@functools.cache
def _config_file() -> Path:
    config_file_paths = [
        env.config_file(),
        env.USER_CONFIG / 'sodalite.conf',
        Path('/etc/sodalite.conf'),
        Path('/usr/local/etc/sodalite.conf'),
        Path('/usr/share/sodalite/sodalite.conf'),
    ]

    for file in config_file_paths:
        if file.exists():
            logger.debug(f"Using config file '{file}'")
            return file
    raise ConfigNotFound()


def _sanitize_keymap(keys: dict[str, str]) -> dict[str, str]:
    # ctrl h equals backspace in terminal emulators
    for action, keybinding in keys.items():
        if keybinding == 'ctrl h':
            keys[action] = 'ctrl h'
    return keys


HooksConfig = dict[str, Optional[dict[str, Union[str, dict[str, str]]]]]


@dataclass
class Configuration:
    hooks: HooksConfig
    keymap: dict[str, str]
    preferred_names: list[str]


@functools.cache
def get() -> Configuration:
    try:
        config_str = _config_file().read_text()
        config_dict = yaml.safe_load(config_str)
        return Configuration(
            hooks=config_dict.get('hooks') or {},
            keymap=_sanitize_keymap(config_dict.get('keymap') or {}),
            preferred_names=[x.lower() for x in config_dict.get('preferred_names')] or [],
        )
    except (ParserError, ScannerError):
        logger.exception(f"Failed to parse config file'{_config_file()}': Invalid yaml.", exc_info=True)
        exit(1)
