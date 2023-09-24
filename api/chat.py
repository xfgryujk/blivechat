# -*- coding: utf-8 -*-
import asyncio
import enum
import json
import logging
import random
import time
import uuid
from typing import *

import aiohttp
import tornado.websocket

import api.base
import blivedm.blivedm.clients.web as dm_web_cli
import config
import services.avatar
import services.chat
import services.translate
import utils.request

logger = logging.getLogger(__name__)


class Command(enum.IntEnum):
    HEARTBEAT = 0
    JOIN_ROOM = 1
    ADD_TEXT = 2
    ADD_GIFT = 3
    ADD_MEMBER = 4
    ADD_SUPER_CHAT = 5
    DEL_SUPER_CHAT = 6
    UPDATE_TRANSLATION = 7
    FATAL_ERROR = 8


class ContentType(enum.IntEnum):
    TEXT = 0
    EMOTICON = 1


class FatalErrorType(enum.IntEnum):
    AUTH_CODE_ERROR = 1


def make_message_body(cmd, data):
    return json.dumps(
        {
            'cmd': cmd,
            'data': data
        }
    ).encode('utf-8')


def make_text_message_data(
    avatar_url: str = services.avatar.DEFAULT_AVATAR_URL,
    timestamp: int = None,
    author_name: str = '',
    author_type: int = 0,
    content: str = '',
    privilege_type: int = 0,
    is_gift_danmaku: bool = False,
    author_level: int = 1,
    is_newbie: bool = False,
    is_mobile_verified: bool = True,
    medal_level: int = 0,
    id_: str = None,
    translation: str = '',
    content_type: int = ContentType.TEXT,
    content_type_params: list = None,
    author_id: int = 0
):
    # 为了节省带宽用list而不是dict
    return [
        # 0: avatarUrl
        avatar_url,
        # 1: timestamp
        timestamp if timestamp is not None else int(time.time()),
        # 2: authorName
        author_name,
        # 3: authorType
        author_type,
        # 4: content
        content,
        # 5: privilegeType
        privilege_type,
        # 6: isGiftDanmaku
        1 if is_gift_danmaku else 0,
        # 7: authorLevel
        author_level,
        # 8: isNewbie
        1 if is_newbie else 0,
        # 9: isMobileVerified
        1 if is_mobile_verified else 0,
        # 10: medalLevel
        medal_level,
        # 11: id
        id_ if id_ is not None else uuid.uuid4().hex,
        # 12: translation
        translation,
        # 13: contentType
        content_type,
        # 14: contentTypeParams
        content_type_params if content_type_params is not None else [],
        # 15: textEmoticons
        [],  # 已废弃，保留
        # 16: authorId
        author_id
    ]


def make_emoticon_params(url):
    return [
        # 0: url
        url,
    ]


def make_translation_message_data(msg_id, translation):
    return [
        # 0: id
        msg_id,
        # 1: translation
        translation,
    ]


class ChatHandler(tornado.websocket.WebSocketHandler):
    HEARTBEAT_INTERVAL = 10
    RECEIVE_TIMEOUT = HEARTBEAT_INTERVAL + 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._heartbeat_timer_handle = None
        self._receive_timeout_timer_handle = None

        self.room_key: Optional[services.chat.RoomKey] = None
        self.auto_translate = False

    def open(self):
        logger.info('client=%s connected', self.request.remote_ip)
        self._heartbeat_timer_handle = asyncio.get_running_loop().call_later(
            self.HEARTBEAT_INTERVAL, self._on_send_heartbeat
        )
        self._refresh_receive_timeout_timer()

    def _on_send_heartbeat(self):
        self.send_cmd_data(Command.HEARTBEAT, {})
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
        logger.info('client=%s timed out', self.request.remote_ip)
        self._receive_timeout_timer_handle = None
        self.close()

    def on_close(self):
        logger.info('client=%s disconnected, room=%s', self.request.remote_ip, self.room_key)
        if self.has_joined_room:
            services.chat.client_room_manager.del_client(self.room_key, self)
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

            if cmd == Command.HEARTBEAT:
                # 超时没有加入房间也断开
                if self.has_joined_room:
                    self._refresh_receive_timeout_timer()

            elif cmd == Command.JOIN_ROOM:
                self._on_join_room_req(body)

            else:
                logger.warning('client=%s unknown cmd=%d, body=%s', self.request.remote_ip, cmd, body)

        except Exception:  # noqa
            logger.exception('client=%s on_message error, message=%s', self.request.remote_ip, message)

    def _on_join_room_req(self, body: dict):
        if self.has_joined_room:
            return
        data = body['data']

        room_key_dict = data.get('roomKey', None)
        if room_key_dict is not None:
            room_key_type = services.chat.RoomKeyType(room_key_dict['type'])
            room_key_value = room_key_dict['value']
            if room_key_type == services.chat.RoomKeyType.ROOM_ID:
                if not isinstance(room_key_value, int):
                    raise TypeError(f'Room key value type error, value={room_key_value}')
            elif room_key_type == services.chat.RoomKeyType.AUTH_CODE:
                if not isinstance(room_key_value, str):
                    raise TypeError(f'Room key value type error, value={room_key_value}')
            else:
                raise ValueError(f'Unknown RoomKeyType={room_key_type}')
        else:
            # 兼容旧版客户端 TODO 过几个版本可以移除
            room_key_type = services.chat.RoomKeyType.ROOM_ID
            room_key_value = int(data['roomId'])
        self.room_key = services.chat.RoomKey(room_key_type, room_key_value)
        logger.info('client=%s joining room %s', self.request.remote_ip, self.room_key)

        try:
            cfg = data['config']
            self.auto_translate = bool(cfg['autoTranslate'])
        except KeyError:
            pass

        services.chat.client_room_manager.add_client(self.room_key, self)
        asyncio.create_task(self._on_joined_room())

        self._refresh_receive_timeout_timer()

    # 跨域测试用
    def check_origin(self, origin):
        if self.application.settings['debug']:
            return True
        return super().check_origin(origin)

    @property
    def has_joined_room(self):
        return self.room_key is not None

    def send_cmd_data(self, cmd, data):
        self.send_body_no_raise(make_message_body(cmd, data))

    def send_body_no_raise(self, body: Union[bytes, str, Dict[str, Any]]):
        try:
            self.write_message(body)
        except tornado.websocket.WebSocketClosedError:
            self.close()

    async def _on_joined_room(self):
        if self.settings['debug']:
            await self._send_test_message()

        # 不允许自动翻译的提示
        if self.auto_translate:
            cfg = config.get_config()
            if (
                cfg.allow_translate_rooms
                # 身份码就不管了吧，反正配置正确的情况下不会看到这个提示
                and self.room_key.type == services.chat.RoomKeyType.ROOM_ID
                and self.room_key.value not in cfg.allow_translate_rooms
            ):
                self.send_cmd_data(Command.ADD_TEXT, make_text_message_data(
                    author_name='blivechat',
                    author_type=2,
                    content='Translation is not allowed in this room. Please download to use translation',
                    author_level=60,
                ))

    # 测试用
    async def _send_test_message(self):
        base_data = {
            'avatarUrl': await services.avatar.get_avatar_url(300474, 'xfgryujk'),
            'timestamp': int(time.time()),
            'authorName': 'xfgryujk',
        }
        text_data = make_text_message_data(
            avatar_url=base_data['avatarUrl'],
            timestamp=base_data['timestamp'],
            author_name=base_data['authorName'],
            content='我能吞下玻璃而不伤身体',
            author_level=60,
        )
        member_data = {
            **base_data,
            'id': uuid.uuid4().hex,
            'privilegeType': 3
        }
        gift_data = {
            **base_data,
            'id': uuid.uuid4().hex,
            'totalCoin': 450000,
            'giftName': '摩天大楼',
            'num': 1
        }
        sc_data = {
            **base_data,
            'id': str(random.randint(1, 65535)),
            'price': 30,
            'content': 'The quick brown fox jumps over the lazy dog',
            'translation': ''
        }
        self.send_cmd_data(Command.ADD_TEXT, text_data)
        text_data[4] = 'te[dog]st'
        text_data[11] = uuid.uuid4().hex
        self.send_cmd_data(Command.ADD_TEXT, text_data)
        text_data[2] = '主播'
        text_data[3] = 3
        text_data[4] = "I can eat glass, it doesn't hurt me."
        text_data[11] = uuid.uuid4().hex
        self.send_cmd_data(Command.ADD_TEXT, text_data)
        self.send_cmd_data(Command.ADD_MEMBER, member_data)
        self.send_cmd_data(Command.ADD_SUPER_CHAT, sc_data)
        sc_data['id'] = str(random.randint(1, 65535))
        sc_data['price'] = 100
        sc_data['content'] = '敏捷的棕色狐狸跳过了懒狗'
        self.send_cmd_data(Command.ADD_SUPER_CHAT, sc_data)
        # self.send_cmd_data(Command.DEL_SUPER_CHAT, {'ids': [sc_data['id']]})
        self.send_cmd_data(Command.ADD_GIFT, gift_data)
        gift_data['id'] = uuid.uuid4().hex
        gift_data['totalCoin'] = 1245000
        gift_data['giftName'] = '小电视飞船'
        self.send_cmd_data(Command.ADD_GIFT, gift_data)


class RoomInfoHandler(api.base.ApiHandler):
    async def get(self):
        room_id = int(self.get_query_argument('roomId'))
        logger.info('client=%s getting room info, room=%d', self.request.remote_ip, room_id)
        room_id, owner_uid = await self._get_room_info(room_id)
        # 连接其他host必须要key
        host_server_list = dm_web_cli.DEFAULT_DANMAKU_SERVER_LIST
        if owner_uid == 0:
            # 缓存3分钟
            self.set_header('Cache-Control', 'private, max-age=180')
        else:
            # 缓存1天
            self.set_header('Cache-Control', 'private, max-age=86400')
        self.write({
            'roomId': room_id,
            'ownerUid': owner_uid,
            'hostServerList': host_server_list
        })

    @staticmethod
    async def _get_room_info(room_id):
        try:
            async with utils.request.http_session.get(
                dm_web_cli.ROOM_INIT_URL,
                headers={
                    **utils.request.BILIBILI_COMMON_HEADERS,
                    'Origin': 'https://live.bilibili.com',
                    'Referer': f'https://live.bilibili.com/{room_id}'
                },
                params={
                    'room_id': room_id
                }
            ) as res:
                if res.status != 200:
                    logger.warning('room=%d _get_room_info failed: %d %s', room_id,
                                   res.status, res.reason)
                    return room_id, 0
                data = await res.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            logger.exception('room=%d _get_room_info failed', room_id)
            return room_id, 0

        if data['code'] != 0:
            logger.warning('room=%d _get_room_info failed: %s', room_id, data['message'])
            return room_id, 0

        room_info = data['data']['room_info']
        return room_info['room_id'], room_info['uid']


class AvatarHandler(api.base.ApiHandler):
    async def get(self):
        uid = int(self.get_query_argument('uid'))
        username = self.get_query_argument('username', '')
        avatar_url = await services.avatar.get_avatar_url_or_none(uid)
        if avatar_url is None:
            avatar_url = services.avatar.get_default_avatar_url(uid, username)
            # 缓存3分钟
            self.set_header('Cache-Control', 'private, max-age=180')
        else:
            # 缓存1天
            self.set_header('Cache-Control', 'private, max-age=86400')
        self.write({'avatarUrl': avatar_url})


class TextEmoticonMappingsHandler(api.base.ApiHandler):
    async def get(self):
        # 缓存1天
        self.set_header('Cache-Control', 'private, max-age=86400')
        cfg = config.get_config()
        self.write({'textEmoticons': cfg.text_emoticons})


ROUTES = [
    (r'/api/chat', ChatHandler),
    (r'/api/room_info', RoomInfoHandler),
    (r'/api/avatar_url', AvatarHandler),
    (r'/api/text_emoticon_mappings', TextEmoticonMappingsHandler),
]
