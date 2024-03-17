# -*- coding: utf-8 -*-
import asyncio
import json
import logging
from typing import *

import tornado.web
import tornado.websocket

import api.base
import api.chat
import blcsdk.models as models
import config
import services.avatar
import services.chat
import services.plugin

logger = logging.getLogger(__name__)


class _AdminHandlerBase(api.base.ApiHandler):
    def prepare(self):
        cfg = config.get_config()
        if not cfg.enable_admin_plugins:
            raise tornado.web.HTTPError(403)

        logger.info('client=%s requesting admin plugin, cls=%s', self.request.remote_ip, type(self).__name__)

        super().prepare()

    def _get_plugin(self):
        plugin_id = self.json_args.get('pluginId', None)
        if not isinstance(plugin_id, str) or plugin_id == '':
            raise tornado.web.MissingArgumentError('pluginId')
        plugin = services.plugin.get_plugin(plugin_id)
        if plugin is None:
            raise tornado.web.HTTPError(404, 'no plugin, plugin_id=%s', plugin_id)
        return plugin


# 不继承_AdminHandlerBase，为了忽略enable_admin_plugins
class PluginsHandler(api.base.ApiHandler):
    async def get(self):
        plugin_dicts = []
        for plugin in services.plugin.iter_plugins():
            plugin_cfg = plugin.config
            plugin_dicts.append({
                'id': plugin.id,
                'name': plugin_cfg.name,
                'version': plugin_cfg.version,
                'author': plugin_cfg.author,
                'description': plugin_cfg.description,
                'enabled': plugin.enabled,
                'isStarted': plugin.is_started,
                'isConnected': plugin.is_connected,
            })
        self.write({'plugins': plugin_dicts})


class EnableHandler(_AdminHandlerBase):
    async def post(self):
        enabled = bool(self.json_args.get('enabled', False))

        plugin = self._get_plugin()
        old_enabled = plugin.enabled
        is_switch_success = True
        msg = ''
        try:
            plugin.enabled = enabled
        except services.plugin.SwitchTooFrequently as e:
            is_switch_success = False
            msg = str(e)
            plugin.enabled = old_enabled
        except services.plugin.SwitchPluginError as e:
            is_switch_success = False
            msg = str(e)
        self.write({
            'enabled': plugin.enabled,
            'isSwitchSuccess': is_switch_success,
            'msg': msg
        })


class OpenAdminUiHandler(_AdminHandlerBase):
    async def post(self):
        plugin = self._get_plugin()
        plugin.send_cmd_data(models.Command.OPEN_PLUGIN_ADMIN_UI, {})
        self.write({})


class _PluginApiHandlerBase(api.base.ApiHandler):
    """给插件用的接口"""
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


class PluginWsHandler(_PluginApiHandlerBase, tornado.websocket.WebSocketHandler):
    HEARTBEAT_INTERVAL = 30
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
        if self._heartbeat_timer_handle is not None:
            self._heartbeat_timer_handle.cancel()
            self._heartbeat_timer_handle = None
        if self._receive_timeout_timer_handle is not None:
            self._receive_timeout_timer_handle.cancel()
            self._receive_timeout_timer_handle = None

    def on_message(self, message):
        try:
            body = json.loads(message)
            cmd = int(body['cmd'])
            data = body['data']

            if cmd == models.Command.HEARTBEAT:
                self._refresh_receive_timeout_timer()
            elif cmd == models.Command.LOG_REQ:
                logger.log(int(data['level']), '[%s] %s', self.plugin.id, data['msg'])
            elif cmd == models.Command.ADD_TEXT_REQ:
                self._on_add_text_req(data)
            else:
                logger.warning('plugin=%s unknown cmd=%d, body=%s', self.plugin.id, cmd, body)

        except Exception:  # noqa
            logger.exception('plugin=%s on_message error, message=%s', self.plugin.id, message)

    def _on_add_text_req(self, data: dict):
        room_key_dict = data['roomKey']
        if room_key_dict is not None:
            room_key = services.chat.RoomKey.from_dict(room_key_dict)
            room = services.chat.client_room_manager.get_room(room_key)
            if room is not None:
                rooms = [room]
            else:
                rooms = []
        else:
            rooms = list(services.chat.client_room_manager.iter_rooms())
        if not rooms:
            return

        author_name = str(data['authorName'])
        if author_name == '':
            author_name = self.plugin.id
        uid = str(data['uid'])
        avatar_url = str(data['avatarUrl'])
        if avatar_url == '':
            avatar_url = services.avatar.get_default_avatar_url(username=author_name)

        data_to_send = api.chat.make_text_message_data(
            content=str(data['content']),
            author_name=author_name,
            uid=uid,
            avatar_url=avatar_url,
            author_type=int(data['authorType']),
            privilege_type=int(data['guardLevel']),
            medal_level=int(data['medalLevel']),
            translation=str(data['translation']),
        )

        body_for_room = api.chat.make_message_body(api.chat.Command.ADD_TEXT, data_to_send)
        for room in rooms:
            room.send_body_no_raise(body_for_room)

            extra = services.chat.make_plugin_msg_extra_from_client_room(room)
            extra['isFromPlugin'] = True
            services.plugin.broadcast_cmd_data(models.Command.ADD_TEXT, data_to_send, extra)

    def send_cmd_data(self, cmd, data, extra: Optional[dict] = None):
        self.send_body_no_raise(make_message_body(cmd, data, extra))

    def send_body_no_raise(self, body: Union[bytes, str, Dict[str, Any]]):
        try:
            self.write_message(body)
        except tornado.websocket.WebSocketClosedError:
            self.close()


class RoomsHandler(_PluginApiHandlerBase):
    async def get(self):
        rooms = [
            {
                'roomId': live_client.room_id,
                'roomKey': live_client.room_key.to_dict(),
            }
            for live_client in services.chat.iter_live_clients()
        ]
        self.write({'rooms': rooms})


ROUTES = [
    (r'/api/plugin/plugins', PluginsHandler),
    (r'/api/plugin/enable_plugin', EnableHandler),
    (r'/api/plugin/open_admin_ui', OpenAdminUiHandler),
    (r'/api/plugin/websocket', PluginWsHandler),
    (r'/api/plugin/rooms', RoomsHandler),
]
