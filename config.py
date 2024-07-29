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


def init(cmd_args):
    if reload(cmd_args):
        return
    logger.warning('Using default config')

    config = AppConfig()
    config.load_cmd_args(cmd_args)

    global _config
    _config = config


def reload(cmd_args):
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
    config.load_cmd_args(cmd_args)

    global _config
    _config = config
    return True


def get_config():
    return _config


class AppConfig:
    def __init__(self):
        self.debug = False
        self.host = '127.0.0.1'
        self.port = 12450
        self.database_url = 'sqlite:///data/database.db'
        self.tornado_xheaders = False
        self.loader_url = ''
        self.open_browser_at_startup = True
        self.enable_upload_file = True
        self.enable_admin_plugins = True

        self.fetch_avatar_max_queue_size = 4
        self.avatar_cache_size = 10000

        self.open_live_access_key_id = ''
        self.open_live_access_key_secret = ''
        self.open_live_app_id = 0

        self.enable_translate = True
        self.allow_translate_rooms = set()
        self.translate_max_queue_size = 10
        self.translation_cache_size = 50000
        self.translator_configs = []

        self.text_emoticons = []

    @property
    def is_open_live_configured(self):
        return (
            self.open_live_access_key_id != '' and self.open_live_access_key_secret != '' and self.open_live_app_id != 0
        )

    def load_cmd_args(self, args):
        if args.host is not None:
            self.host = args.host
        if args.port is not None:
            self.port = args.port
        self.debug = args.debug

    def load(self, path):
        try:
            config = configparser.ConfigParser()
            config.read(path, 'utf-8-sig')

            self._load_app_config(config)
            self._load_translator_configs(config)
            self._load_text_emoticons(config)
        except Exception:  # noqa
            logger.exception('Failed to load config:')
            return False
        return True

    def _load_app_config(self, config: configparser.ConfigParser):
        app_section = config['app']
        self.host = app_section.get('host', self.host)
        self.port = app_section.getint('port', self.port)
        self.database_url = app_section.get('database_url', self.database_url)
        self.tornado_xheaders = app_section.getboolean('tornado_xheaders', self.tornado_xheaders)
        self.loader_url = app_section.get('loader_url', self.loader_url)
        if self.loader_url == '{local_loader}':
            self.loader_url = self._get_local_loader_url()
        self.open_browser_at_startup = app_section.getboolean('open_browser_at_startup', self.open_browser_at_startup)
        self.enable_upload_file = app_section.getboolean('enable_upload_file', self.enable_upload_file)
        self.enable_admin_plugins = app_section.getboolean('enable_admin_plugins', self.enable_admin_plugins)

        self.fetch_avatar_max_queue_size = app_section.getint(
            'fetch_avatar_max_queue_size', self.fetch_avatar_max_queue_size
        )
        self.avatar_cache_size = app_section.getint('avatar_cache_size', self.avatar_cache_size)

        self.open_live_access_key_id = app_section.get('open_live_access_key_id', self.open_live_access_key_id)
        self.open_live_access_key_secret = app_section.get(
            'open_live_access_key_secret', self.open_live_access_key_secret
        )
        self.open_live_app_id = app_section.getint('open_live_app_id', self.open_live_app_id)

        self.enable_translate = app_section.getboolean('enable_translate', self.enable_translate)
        self.allow_translate_rooms = _str_to_list(app_section.get('allow_translate_rooms', ''), int, set)
        self.translate_max_queue_size = app_section.getint('translate_max_queue_size', self.translate_max_queue_size)
        self.translation_cache_size = app_section.getint('translation_cache_size', self.translation_cache_size)

    @staticmethod
    def _get_local_loader_url():
        url = os.path.abspath(os.path.join(DATA_PATH, 'loader.html'))
        url = url.replace('\\', '/')
        if not url.startswith('/'):  # Windows
            url = '/' + url
        url = 'file://' + url
        return url

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
                }
                if type_ in ('TencentTranslateFree', 'BilibiliTranslateFree'):
                    doc_url = (
                        'https://github.com/xfgryujk/blivechat/wiki/%E9%85%8D%E7%BD%AE%E5%AE%98%E6%96%B9'
                        '%E7%BF%BB%E8%AF%91%E6%8E%A5%E5%8F%A3'
                    )
                    logger.warning('%s is deprecated, please see %s', type_, doc_url)
                    continue
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
                elif type_ == 'GeminiTranslate':
                    translator_config['proxy'] = section['proxy']
                    translator_config['api_key'] = section['api_key']
                    translator_config['model_code'] = section['model_code']
                    translator_config['prompt'] = section['prompt'].replace('\n', ' ').replace('\\n', '\n')
                    translator_config['temperature'] = section.getfloat('temperature')
                else:
                    raise ValueError(f'Invalid translator type: {type_}')
            except Exception:  # noqa
                logger.exception('Failed to load translator=%s config:', section_name)
                continue

            translator_configs.append(translator_config)
        self.translator_configs = translator_configs

    def _load_text_emoticons(self, config: configparser.ConfigParser):
        mappings_section = config['text_emoticon_mappings']
        text_emoticons = []
        for value in mappings_section.values():
            keyword, _, url = value.partition(',')
            text_emoticons.append({'keyword': keyword, 'url': url})
        self.text_emoticons = text_emoticons


def _str_to_list(value, item_type: Type = str, container_type: Type = list):
    value = value.strip()
    if value == '':
        return container_type()
    items = value.split(',')
    items = map(lambda item: item.strip(), items)
    if item_type is not str:
        items = map(lambda item: item_type(item), items)
    return container_type(items)
