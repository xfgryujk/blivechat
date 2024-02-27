# -*- coding: utf-8 -*-
import os
from typing import *

BASE_PATH = os.path.realpath(os.getcwd())
LOG_PATH = os.path.join(BASE_PATH, 'log')

_config: Optional['AppConfig'] = None


def init():
    global _config
    _config = AppConfig()
    # TODO 读配置文件


def get_config():
    return _config


class AppConfig:
    def __init__(self):
        self.tts_voice_id: Optional[str] = None
        self.tts_rate = 250
        self.tts_volume = 1.0

        self.max_tts_queue_size = 5

        self.template_text = '{author_name} 说：{content}'
        self.template_free_gift = '{author_name} 赠送了{num}个{gift_name}，总价{total_coin}银瓜子'
        self.template_paid_gift = '{author_name} 赠送了{num}个{gift_name}，总价{price}元'
        self.template_member = '{author_name} 购买了{num}{unit} {guard_name}'
        self.template_super_chat = '{author_name} 发送了{price}元的醒目留言：{content}'
