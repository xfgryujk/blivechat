# -*- coding: utf-8 -*-

import configparser
import logging
import os
from typing import *

logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join('data', 'config.ini')

_config: Optional['AppConfig'] = None


def init():
    if reload():
        return
    logger.warning('Using default config')
    global _config
    _config = AppConfig()


def reload():
    config = AppConfig()
    if not config.load(CONFIG_PATH):
        return False
    global _config
    _config = config
    return True


def get_config():
    return _config


class AppConfig:
    def __init__(self):
        self.database_url = 'sqlite:///data/database.db'
        self.enable_translate = True
        self.allow_translate_rooms = {}

    def load(self, path):
        config = configparser.ConfigParser()
        config.read(path)
        try:
            app_section = config['app']
            self.database_url = app_section['database_url']
            self.enable_translate = app_section.getboolean('enable_translate')
            allow_translate_rooms = app_section['allow_translate_rooms'].strip()
            if allow_translate_rooms == '':
                self.allow_translate_rooms = {}
            else:
                allow_translate_rooms = allow_translate_rooms.split(',')
                self.allow_translate_rooms = set(map(lambda id_: int(id_.strip()), allow_translate_rooms))
        except (KeyError, ValueError):
            logger.exception('Failed to load config:')
            return False
        return True
