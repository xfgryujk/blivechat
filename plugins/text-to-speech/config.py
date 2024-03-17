# -*- coding: utf-8 -*-
import configparser
import logging
import os
from typing import *

logger = logging.getLogger('text-to-speech.' + __name__)

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_PATH = os.path.join(BASE_PATH, 'log')
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
        self.tts_voice_id = ''
        self.tts_rate = 250
        self.tts_volume = 1.0

        self.max_tts_queue_size = 5

        self.template_text = '{author_name} 说，{content}'
        # self.template_free_gift = '{author_name} 赠送了{num}个{gift_name}，总价{total_coin}银瓜子'
        self.template_free_gift = '{author_name} 赠送了{num}个{gift_name}'
        self.template_paid_gift = '{author_name} 赠送了{num}个{gift_name}，总价{price:.1f}元'
        self.template_member = '{author_name} 购买了{num}{unit} {guard_name}，总价{price:.1f}元'
        self.template_super_chat = '{author_name} 发送了{price}元的醒目留言，{content}'

    def load(self, path):
        try:
            config = configparser.ConfigParser()
            config.read(path, 'utf-8-sig')

            self._load_app_config(config)
        except Exception:  # noqa
            logger.exception('Failed to load config:')
            return False
        return True

    def _load_app_config(self, config: configparser.ConfigParser):
        app_section = config['app']
        self.tts_voice_id = app_section.get('tts_voice_id', self.tts_voice_id)
        self.tts_rate = app_section.getint('tts_rate', self.tts_rate)
        self.tts_volume = app_section.getfloat('tts_volume', self.tts_volume)

        self.max_tts_queue_size = app_section.getint('max_tts_queue_size', self.max_tts_queue_size)

        self.template_text = app_section.get('template_text', self.template_text)
        self.template_free_gift = app_section.get('template_free_gift', self.template_free_gift)
        self.template_paid_gift = app_section.get('template_paid_gift', self.template_paid_gift)
        self.template_member = app_section.get('template_member', self.template_member)
        self.template_super_chat = app_section.get('template_super_chat', self.template_super_chat)
