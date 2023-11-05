# -*- coding: utf-8 -*-
import __main__
import logging
from typing import *

import blcsdk
import blcsdk.models as sdk_models
from blcsdk import client as cli

logger = logging.getLogger(__name__)

_msg_handler: Optional['MsgHandler'] = None


async def init():
    global _msg_handler
    _msg_handler = MsgHandler()
    blcsdk.set_msg_handler(_msg_handler)


class MsgHandler(blcsdk.BaseHandler):
    def on_client_stopped(self, client: cli.BlcPluginClient, exception: Optional[Exception]):
        logger.info('blivechat disconnected')
        __main__.start_shut_down()

    def _on_add_text(self, client: cli.BlcPluginClient, message: sdk_models.AddTextMsg):
        """收到弹幕"""

    def _on_add_gift(self, client: cli.BlcPluginClient, message: sdk_models.AddGiftMsg):
        """有人送礼"""

    def _on_add_member(self, client: cli.BlcPluginClient, message: sdk_models.AddMemberMsg):
        """有人上舰"""

    def _on_add_super_chat(self, client: cli.BlcPluginClient, message: sdk_models.AddSuperChatMsg):
        """醒目留言"""

    def _on_del_super_chat(self, client: cli.BlcPluginClient, message: sdk_models.DelSuperChatMsg):
        """删除醒目留言"""

    def _on_update_translation(self, client: cli.BlcPluginClient, message: sdk_models.UpdateTranslationMsg):
        """更新翻译"""
