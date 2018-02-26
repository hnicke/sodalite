from _yaml import ScannerError

import yaml

import environment
from mylogger import logger


class InvalidConfiguration(Exception):
    pass


class Config:
    def __init__(self):
        try:
            with open(environment.config_path) as f:
                # use safe_load instead load
                config = yaml.safe_load(f)
                self.hooks = config['hooks']
        except ScannerError:
            logger.exception("Error while parsing config file '{}'".format(environment.config_path))
            raise InvalidConfiguration
