# -*- coding: utf-8 -*-

import configparser
import logging
import os
from typing import *

logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join('data', 'config.ini')

_config: Optional['AppConfig'] = None


def init():
    reload()


def reload():
    config = AppConfig()
    if config.load(CONFIG_PATH):
        global _config
        _config = config


def get_config():
    return _config


class AppConfig:
    def __init__(self):
        self.database_url = 'sqlite:///data/database.db'
        self.enable_translate = True

    def load(self, path):
        config = configparser.ConfigParser()
        config.read(path)
        try:
            app_section = config['app']
            self.database_url = app_section['database_url']
            self.enable_translate = app_section.getboolean('enable_translate')
        except (KeyError, ValueError):
            logger.exception('Failed to load config:')
            return False
        return True
