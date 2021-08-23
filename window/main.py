# -*- coding: utf-8 -*-

import json
import json.decoder
import logging
import os
import sys
from argparse import Namespace
from typing import Optional

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication

import update
from window.console import ConsoleWindow

GUI_CONFIG_PATH = os.path.join('data', 'gui.config.json')

configs = {
    'roomId': '1',
    'roomConfig': {
        'showDanmaku': True,
        'mergeSimilarDanmaku': False,
        'maxNumber': 60,
        'showGift': True,
        'showGiftName': False,
        'mergeGift': True,
        'minGiftPrice': 7,
        'blockGiftDanmaku': True,
        'blockNewbie': False,
        'blockNotMobileVerified': False,
        'blockLevel': 0,
        'blockMedalLevel': 0,
        'blockKeywords': '',
        'blockUsers': '',
        'relayMessagesByServer': False,
        'autoTranslate': False,
        'giftUsernamePronunciation': ''
    },
    'css': [],
    'float': {
        'x': 100,
        'y': 100,
        'width': 400,
        'height': 800,
        'transparent': 100,
        'scale': 100,
        'mindedTransparent': False
    }
}
room_url: str
config_url = f'http://localhost:12450/?_v={update.VERSION}'
logger = logging.getLogger(__name__)
app: Optional['QApplication'] = None
console: Optional['ConsoleWindow'] = None
args: Optional['Namespace'] = None


def merge(origin: dict, new: dict):
    for key in origin:
        if key in new:
            if isinstance(new[key], type(origin[key])):
                if isinstance(origin[key], dict):
                    merge(origin[key], new[key])
                else:
                    origin[key] = new[key]
            else:
                try:
                    origin[key] = type(origin[key])(new[key])
                except ValueError:
                    logger.error('Unknown config value: %s(%s), excepted: %s(%s)' % (
                        new[key], type(new[key]), origin[key], type(origin[key])
                    ))


def encode_q_url(obj):
    if isinstance(obj, QUrl):
        return {'__QUrl__': obj.url()}
    else:
        raise TypeError(repr(obj) + " is not JSON serializable")


def decode_q_url(dct):
    if '__QUrl__' in dct:
        return QUrl(dct['__QUrl__'])
    else:
        return dct


def save_config():
    with open(GUI_CONFIG_PATH, 'w', encoding='UTF-8') as file:
        json.dump(configs, file, ensure_ascii=False, default=encode_q_url, indent=2)


def load_config():
    if os.path.exists(GUI_CONFIG_PATH):
        with open(GUI_CONFIG_PATH, 'r', encoding='UTF-8') as file:
            merge(configs, json.load(file, object_hook=decode_q_url))
    else:
        save_config()


def init(args_):
    global app, console, args
    args = args_
    app_argv = sys.argv.copy()
    load_config()
    if args_.debug:
        app_argv += ['--remote-debugging-port=9222']
        print('Remote WebViews DevTools:')
        print('- "chrome://inspect/#devices", Chromium based browser.')
        print('- "http://localhost:9222/", any browser.')
    app_argv += [
        # https://peter.sh/experiments/chromium-command-line-switches/
        '--disable-web-security',  # 禁用网页安全机制：跨域
        '--allow-insecure-websocket-from-https-origin',  # 允许https页面访问不加密的websocket： https页面使用ws消息链连接
    ]
    app = QApplication(app_argv)
    app.setQuitOnLastWindowClosed(False)
    console = ConsoleWindow()


def loop():
    code = app.exec_()
    save_config()
    sys.exit(code)
