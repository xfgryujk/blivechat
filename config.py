# -*- coding: utf-8 -*-
import configparser
import logging
import os
from typing import *

logger = logging.getLogger(__name__)

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
WEB_ROOT = os.path.join(BASE_PATH, 'frontend', 'dist')
DATA_PATH = os.path.join(BASE_PATH, 'data')

CONFIG_PATH_LIST = [
    os.path.join(DATA_PATH, 'config.ini'),
    os.path.join(DATA_PATH, 'config.example.ini')
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
        self.enable_upload_file = True

        self.fetch_avatar_interval = 3.5
        self.fetch_avatar_max_queue_size = 2
        self.avatar_cache_size = 50000

        self.enable_translate = True
        self.allow_translate_rooms = set()
        self.translation_cache_size = 50000
        self.translator_configs = []

        self.bilibili_cookies_file = ''

    def load(self, path):
        try:
            config = configparser.ConfigParser()
            config.read(path, 'utf-8-sig')

            self._load_app_config(config)
            self._load_translator_configs(config)
        except Exception:  # noqa
            logger.exception('Failed to load config:')
            return False
        return True

    def _load_app_config(self, config: configparser.ConfigParser):
        app_section = config['app']
        self.database_url = app_section.get('database_url', self.database_url)
        self.tornado_xheaders = app_section.getboolean('tornado_xheaders', fallback=self.tornado_xheaders)
        self.loader_url = app_section.get('loader_url', self.loader_url)
        self.enable_upload_file = app_section.getboolean('enable_upload_file', fallback=self.enable_upload_file)

        self.fetch_avatar_interval = app_section.getfloat('fetch_avatar_interval', fallback=self.fetch_avatar_interval)
        self.fetch_avatar_max_queue_size = app_section.getint('fetch_avatar_max_queue_size',
                                                              fallback=self.fetch_avatar_max_queue_size)
        self.avatar_cache_size = app_section.getint('avatar_cache_size', fallback=self.avatar_cache_size)

        self.enable_translate = app_section.getboolean('enable_translate', fallback=self.enable_translate)
        self.allow_translate_rooms = _str_to_list(app_section.get('allow_translate_rooms', ''), int, set)
        self.translation_cache_size = app_section.getint('translation_cache_size', self.translation_cache_size)

        self.bilibili_cookies_file = app_section.get('bilibili_cookies_file', fallback=self.bilibili_cookies_file)

    def _load_translator_configs(self, config: configparser.ConfigParser):
        app_section = config['app']
        section_names = _str_to_list(app_section.get('translator_configs', ''))
        translator_configs = []
        for section_name in section_names:
            try:
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
            except Exception:  # noqa
                logger.exception('Failed to load translator=%s config:', section_name)
                continue

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
