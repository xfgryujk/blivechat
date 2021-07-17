# -*- coding: utf-8 -*-

import configparser
import logging
import os
from typing import *

logger = logging.getLogger(__name__)

CONFIG_PATH_LIST = [
    os.path.join('data', 'config.ini'),
    os.path.join('data', 'config.example.ini')
]

_config: Optional['AppConfig'] = None


def init():
    if reload():
        return
    logger.warning('Using default config')
    global _config
    _config = AppConfig()


def reload():
    config_path = ''
    for path in CONFIG_PATH_LIST:
        if os.path.exists(path):
            config_path = path
            break
    if config_path == '':
        return False

    config = AppConfig()
    if not config.load(config_path):
        return False
    global _config
    _config = config
    return True


def get_config():
    return _config


class AppConfig:
    def __init__(self):
        self.database_url = 'sqlite:///data/database.db'
        self.tornado_xheaders = False
        self.loader_url = ''

        self.fetch_avatar_interval = 3.5
        self.fetch_avatar_max_queue_size = 2
        self.avatar_cache_size = 50000

        self.enable_translate = True
        self.allow_translate_rooms = set()
        self.translation_cache_size = 50000
        self.translator_configs = []

    def load(self, path):
        try:
            config = configparser.ConfigParser()
            config.read(path, 'utf-8')

            self._load_app_config(config)
            self._load_translator_configs(config)
        except Exception:
            logger.exception('Failed to load config:')
            return False
        return True

    def _load_app_config(self, config):
        app_section = config['app']
        self.database_url = app_section['database_url']
        self.tornado_xheaders = app_section.getboolean('tornado_xheaders')
        self.loader_url = app_section['loader_url']

        self.fetch_avatar_interval = app_section.getfloat('fetch_avatar_interval')
        self.fetch_avatar_max_queue_size = app_section.getint('fetch_avatar_max_queue_size')
        self.avatar_cache_size = app_section.getint('avatar_cache_size')

        self.enable_translate = app_section.getboolean('enable_translate')
        self.allow_translate_rooms = _str_to_list(app_section['allow_translate_rooms'], int, set)
        self.translation_cache_size = app_section.getint('translation_cache_size')

    def _load_translator_configs(self, config):
        app_section = config['app']
        section_names = _str_to_list(app_section['translator_configs'])
        translator_configs = []
        for section_name in section_names:
            section = config[section_name]
            type_ = section['type']

            translator_config = {
                'type': type_,
                'query_interval': section.getfloat('query_interval'),
                'max_queue_size': section.getint('max_queue_size')
            }
            if type_ == 'TencentTranslateFree':
                translator_config['source_language'] = section['source_language']
                translator_config['target_language'] = section['target_language']
            elif type_ == 'BilibiliTranslateFree':
                pass
            elif type_ == 'TencentTranslate':
                translator_config['source_language'] = section['source_language']
                translator_config['target_language'] = section['target_language']
                translator_config['secret_id'] = section['secret_id']
                translator_config['secret_key'] = section['secret_key']
                translator_config['region'] = section['region']
            elif type_ == 'BaiduTranslate':
                translator_config['source_language'] = section['source_language']
                translator_config['target_language'] = section['target_language']
                translator_config['app_id'] = section['app_id']
                translator_config['secret'] = section['secret']
            else:
                raise ValueError(f'Invalid translator type: {type_}')

            translator_configs.append(translator_config)
        self.translator_configs = translator_configs


def _str_to_list(value, item_type: Type = str, container_type: Type = list):
    value = value.strip()
    if value == '':
        return container_type()
    items = value.split(',')
    items = map(lambda item: item.strip(), items)
    if item_type is not str:
        items = map(lambda item: item_type(item), items)
    return container_type(items)
