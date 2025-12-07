# -*- coding: utf-8 -*-
import logging
from typing import *

import app
import blcsdk
import blcsdk.models as sdk_models

logger = logging.getLogger('login.' + __name__)

_msg_handler: Optional['MsgHandler'] = None


async def init():
    global _msg_handler
    _msg_handler = MsgHandler()
    blcsdk.set_msg_handler(_msg_handler)


def shut_down():
    blcsdk.set_msg_handler(None)


class MsgHandler(blcsdk.BaseHandler):
    def on_client_stopped(self, client: blcsdk.BlcPluginClient, exception: Optional[Exception]):
        logger.info('blivechat disconnected')
        app.get_app().start_shut_down()

    def _on_open_plugin_admin_ui(
        self, client: blcsdk.BlcPluginClient, message: sdk_models.OpenPluginAdminUiMsg, extra: sdk_models.ExtraData
    ):
        app.get_app().open_admin_ui()
