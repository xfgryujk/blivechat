# -*- coding: utf-8 -*-
import __main__
import logging
import os
import subprocess
import sys
from typing import *

import blcsdk
import blcsdk.models as sdk_models
import config
import tts

logger = logging.getLogger('text-to-speech.' + __name__)

_msg_handler: Optional['MsgHandler'] = None


def init():
    global _msg_handler
    _msg_handler = MsgHandler()
    blcsdk.set_msg_handler(_msg_handler)


def shut_down():
    blcsdk.set_msg_handler(None)


class MsgHandler(blcsdk.BaseHandler):
    def on_client_stopped(self, client: blcsdk.BlcPluginClient, exception: Optional[Exception]):
        logger.info('blivechat disconnected')
        __main__.start_shut_down()

    def _on_open_plugin_admin_ui(
        self, client: blcsdk.BlcPluginClient, message: sdk_models.OpenPluginAdminUiMsg, extra: sdk_models.ExtraData
    ):
        config_path = ''
        for path in config.CONFIG_PATH_LIST:
            if os.path.exists(path):
                config_path = path
                break
        if config_path == '':
            logger.warning('Config file not found, candidates: %s', config.CONFIG_PATH_LIST)
            return

        if sys.platform == 'win32':
            subprocess.run(['explorer', '/select,' + config_path])
        else:
            logger.info('Config path is "%s"', config_path)

    def _on_add_text(self, client: blcsdk.BlcPluginClient, message: sdk_models.AddTextMsg, extra: sdk_models.ExtraData):
        if extra.is_from_plugin:
            return
        cfg = config.get_config()
        if cfg.template_text == '':
            return

        text = cfg.template_text.format(
            author_name=message.author_name,
            content=message.content,
        )
        tts.say_text(text)

    def _on_add_gift(self, client: blcsdk.BlcPluginClient, message: sdk_models.AddGiftMsg, extra: sdk_models.ExtraData):
        if extra.is_from_plugin:
            return
        cfg = config.get_config()
        is_paid_gift = message.total_coin != 0
        template = cfg.template_paid_gift if is_paid_gift else cfg.template_free_gift
        if template == '':
            return

        task = tts.GiftTtsTask(
            priority=tts.Priority.HIGH if is_paid_gift else tts.Priority.NORMAL,
            author_name=message.author_name,
            num=message.num,
            gift_name=message.gift_name,
            price=message.total_coin / 1000,
            total_coin=message.total_coin if is_paid_gift else message.total_free_coin,
        )
        tts.say(task)

    def _on_add_member(
        self, client: blcsdk.BlcPluginClient, message: sdk_models.AddMemberMsg, extra: sdk_models.ExtraData
    ):
        if extra.is_from_plugin:
            return
        cfg = config.get_config()
        if cfg.template_member == '':
            return

        if message.privilege_type == sdk_models.GuardLevel.LV1:
            guard_name = '舰长'
        elif message.privilege_type == sdk_models.GuardLevel.LV2:
            guard_name = '提督'
        elif message.privilege_type == sdk_models.GuardLevel.LV3:
            guard_name = '总督'
        else:
            guard_name = '未知舰队等级'

        text = cfg.template_member.format(
            author_name=message.author_name,
            num=message.num,
            unit=message.unit,
            guard_name=guard_name,
            price=message.total_coin / 1000,
            total_coin=message.total_coin,
        )
        tts.say_text(text, tts.Priority.HIGH)

    def _on_add_super_chat(
        self, client: blcsdk.BlcPluginClient, message: sdk_models.AddSuperChatMsg, extra: sdk_models.ExtraData
    ):
        if extra.is_from_plugin:
            return
        cfg = config.get_config()
        if cfg.template_super_chat == '':
            return

        text = cfg.template_super_chat.format(
            author_name=message.author_name,
            price=message.price,
            content=message.content,
        )
        tts.say_text(text, tts.Priority.HIGH)
