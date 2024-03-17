# -*- coding: utf-8 -*-
import configparser
import logging
import os
from typing import *

import pubsub.pub as pub

logger = logging.getLogger('native-ui.' + __name__)

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_PATH = os.path.join(BASE_PATH, 'log')
DATA_PATH = os.path.join(BASE_PATH, 'data')

SAVE_CONFIG_PATH = os.path.join(DATA_PATH, 'config.ini')
CONFIG_PATH_LIST = [
    SAVE_CONFIG_PATH,
    os.path.join(DATA_PATH, 'config.example.ini')
]

BLC_ICON_PATH = os.path.join(DATA_PATH, 'blivechat.ico')

_config: Optional['AppConfig'] = None


def init():
    if reload():
        return
    logger.warning('Using default config')
    set_config(AppConfig())


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

    set_config(config)
    return True


def get_config():
    return _config


def set_config(new_config: 'AppConfig'):
    global _config
    old_config = _config
    _config = new_config

    if old_config is not None and new_config is not old_config:
        pub.sendMessage('config_change', new_config=new_config, old_config=old_config)


class AppConfig:
    def __init__(self):
        self.room_opacity = 100

        self.chat_url_params = self._get_default_url_params()
        self.paid_url_params = self._get_default_url_params()

    @staticmethod
    def _get_default_url_params():
        return {
            'minGiftPrice': '0',
            'showGiftName': 'true',
            'maxNumber': '200',
        }

    def is_url_params_changed(self, other: 'AppConfig'):
        return self.chat_url_params != other.chat_url_params or self.paid_url_params != other.paid_url_params

    def load(self, path):
        try:
            config = configparser.ConfigParser()
            config.read(path, 'utf-8-sig')

            self._load_ui_config(config)
            self._load_url_params(config)
        except Exception:  # noqa
            logger.exception('Failed to load config:')
            return False
        return True

    def save(self, path):
        try:
            config = configparser.ConfigParser()

            self._save_ui_config(config)
            self._save_url_params(config)

            tmp_path = path + '.tmp'
            with open(tmp_path, 'w', encoding='utf-8-sig') as f:
                config.write(f)
            os.replace(tmp_path, path)
        except Exception:  # noqa
            logger.exception('Failed to save config:')
            return False
        return True

    def _load_ui_config(self, config: configparser.ConfigParser):
        ui_section = config['ui']
        self.room_opacity = ui_section.getint('room_opacity', self.room_opacity)

    def _save_ui_config(self, config: configparser.ConfigParser):
        config['ui'] = {
            'room_opacity': str(self.room_opacity),
        }

    def _load_url_params(self, config: configparser.ConfigParser):
        self.chat_url_params = self._section_to_url_params(config['chat_url_params'])
        self.paid_url_params = self._section_to_url_params(config['paid_url_params'])

    @staticmethod
    def _section_to_url_params(section: configparser.SectionProxy):
        params = {}
        for line in section.values():
            key, _, value = line.partition('=')
            params[key.strip()] = value.strip()
        return params

    def _save_url_params(self, config: configparser.ConfigParser):
        config['chat_url_params'] = self._url_params_to_section(self.chat_url_params)
        config['paid_url_params'] = self._url_params_to_section(self.paid_url_params)

    @staticmethod
    def _url_params_to_section(url_params: dict):
        return {
            str(index): f'{key} = {value}'
            for index, (key, value) in enumerate(url_params.items(), 1)
        }
