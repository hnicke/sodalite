import logging

import yaml
from yaml.scanner import ScannerError

from util import environment

logger = logging.getLogger(__name__)


class InvalidConfiguration(Exception):
    pass


try:
    with open(environment.config_file) as f:
        # use safe_load instead load
        config_dict = yaml.safe_load(f)
        hooks = config_dict['hooks']
except ScannerError:
    logger.exception("Error while parsing config file '{}'".format(environment.config_file))
    raise InvalidConfiguration
