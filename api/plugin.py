# -*- coding: utf-8 -*-
import asyncio
import json
import logging
from typing import *

import tornado.web
import tornado.websocket

import api.base
import blcsdk.models as models
import services.plugin

logger = logging.getLogger(__name__)


class _PluginHandlerBase(api.base.ApiHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin: Optional[services.plugin.Plugin] = None

    def prepare(self):
        try:
            auth = self.request.headers['Authorization']
            if not auth.startswith('Bearer '):
                raise ValueError(f'Bad authorization: {auth}')
            token = auth[7:]

            self.plugin = services.plugin.get_plugin_by_token(token)
            if self.plugin is None:
                raise ValueError(f'Token error: {token}')
        except (KeyError, ValueError) as e:
            logger.warning('client=%s failed to find plugin: %r', self.request.remote_ip, e)
            raise tornado.web.HTTPError(403)

        super().prepare()


def make_message_body(cmd, data, extra: Optional[dict] = None):
    body = {'cmd': cmd, 'data': data}
    if extra:
        body['extra'] = extra
    return json.dumps(body).encode('utf-8')


class PluginWsHandler(_PluginHandlerBase, tornado.websocket.WebSocketHandler):
    HEARTBEAT_INTERVAL = 10
    RECEIVE_TIMEOUT = HEARTBEAT_INTERVAL + 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._heartbeat_timer_handle = None
        self._receive_timeout_timer_handle = None

    def open(self):
        logger.info('plugin=%s connected, client=%s', self.plugin.id, self.request.remote_ip)
        self._heartbeat_timer_handle = asyncio.get_running_loop().call_later(
            self.HEARTBEAT_INTERVAL, self._on_send_heartbeat
        )
        self._refresh_receive_timeout_timer()

        self.plugin.on_client_connect(self)

    def _on_send_heartbeat(self):
        self.send_cmd_data(models.Command.HEARTBEAT, {})
        self._heartbeat_timer_handle = asyncio.get_running_loop().call_later(
            self.HEARTBEAT_INTERVAL, self._on_send_heartbeat
        )

    def _refresh_receive_timeout_timer(self):
        if self._receive_timeout_timer_handle is not None:
            self._receive_timeout_timer_handle.cancel()
        self._receive_timeout_timer_handle = asyncio.get_running_loop().call_later(
            self.RECEIVE_TIMEOUT, self._on_receive_timeout
        )

    def _on_receive_timeout(self):
        logger.info('plugin=%s timed out', self.plugin.id)
        self._receive_timeout_timer_handle = None
        self.close()

    def on_close(self):
        logger.info('plugin=%s disconnected', self.plugin.id)
        self.plugin.on_client_close(self)

    def send_cmd_data(self, cmd, data, extra: Optional[dict] = None):
        self.send_body_no_raise(make_message_body(cmd, data, extra))

    def send_body_no_raise(self, body: Union[bytes, str, Dict[str, Any]]):
        try:
            self.write_message(body)
        except tornado.websocket.WebSocketClosedError:
            self.close()


ROUTES = [
    (r'/api/plugin/websocket', PluginWsHandler),
]
