import logging
import sys

import yaml
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from util import environment

logger = logging.getLogger(__name__)


class InvalidConfiguration(Exception):
    pass


try:
    with open(environment.config_file) as f:
        # use safe_load instead load
        config_dict = yaml.safe_load(f)
        hooks = config_dict.setdefault('hooks', {})
        keymap = config_dict.get('keymap')
        if not keymap:
            keymap = {}
except ScannerError:
    message = "Error while parsing config file '{}'".format(environment.config_file)
    print(message, file=sys.stderr)
    logger.exception(message)
    exit(1)
except ParserError:
    message = f"Invalid configuration file '{environment.config_file}': Faulty syntax."
    print(message, file=sys.stderr)
    logger.exception(message)
    exit(1)
