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
import blivedm.blivedm as blivedm
import blivedm.blivedm.client as blivedm_client
import config
import models.avatar
import models.translate

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


class ContentType(enum.IntEnum):
    TEXT = 0
    EMOTICON = 1


_http_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))

room_manager: Optional['RoomManager'] = None


def init():
    global room_manager
    room_manager = RoomManager()


class Room(blivedm.BLiveClient, blivedm.BaseHandler):
    HEARTBEAT_INTERVAL = 10

    # 重新定义XXX_callback是为了减少对字段名的依赖，防止B站改字段名
    def __danmu_msg_callback(self, client: blivedm.BLiveClient, command: dict):
        info = command['info']
        if len(info[3]) != 0:
            medal_level = info[3][0]
            medal_room_id = info[3][3]
        else:
            medal_level = 0
            medal_room_id = 0

        message = blivedm.DanmakuMessage(
            timestamp=info[0][4],
            msg_type=info[0][9],
            dm_type=info[0][12],
            emoticon_options=info[0][13],

            msg=info[1],

            uid=info[2][0],
            uname=info[2][1],
            admin=info[2][2],
            urank=info[2][5],
            mobile_verify=info[2][6],

            medal_level=medal_level,
            medal_room_id=medal_room_id,

            user_level=info[4][0],

            privilege_type=info[7],
        )
        return self._on_danmaku(client, message)

    def __send_gift_callback(self, client: blivedm.BLiveClient, command: dict):
        data = command['data']
        message = blivedm.GiftMessage(
            gift_name=data['giftName'],
            num=data['num'],
            uname=data['uname'],
            face=data['face'],
            uid=data['uid'],
            timestamp=data['timestamp'],
            coin_type=data['coin_type'],
            total_coin=data['total_coin'],
        )
        return self._on_gift(client, message)

    def __guard_buy_callback(self, client: blivedm.BLiveClient, command: dict):
        data = command['data']
        message = blivedm.GuardBuyMessage(
            uid=data['uid'],
            username=data['username'],
            guard_level=data['guard_level'],
            start_time=data['start_time'],
        )
        return self._on_buy_guard(client, message)

    def __super_chat_message_callback(self, client: blivedm.BLiveClient, command: dict):
        data = command['data']
        message = blivedm.SuperChatMessage(
            price=data['price'],
            message=data['message'],
            start_time=data['start_time'],
            id_=data['id'],
            uid=data['uid'],
            uname=data['user_info']['uname'],
            face=data['user_info']['face'],
        )
        return self._on_super_chat(client, message)

    _CMD_CALLBACK_DICT = {
        **blivedm.BaseHandler._CMD_CALLBACK_DICT,
        'DANMU_MSG': __danmu_msg_callback,
        'SEND_GIFT': __send_gift_callback,
        'GUARD_BUY': __guard_buy_callback,
        'SUPER_CHAT_MESSAGE': __super_chat_message_callback
    }

    def __init__(self, room_id):
        super().__init__(room_id, session=_http_session, heartbeat_interval=self.HEARTBEAT_INTERVAL)
        self.add_handler(self)
        self.clients: List['ChatHandler'] = []
        self.auto_translate_count = 0

    async def init_room(self):
        await super().init_room()
        return True

    def send_message(self, cmd, data):
        body = json.dumps({'cmd': cmd, 'data': data})
        for client in self.clients:
            try:
                client.write_message(body)
            except tornado.websocket.WebSocketClosedError:
                room_manager.del_client(self.room_id, client)

    def send_message_if(self, can_send_func: Callable[['ChatHandler'], bool], cmd, data):
        body = json.dumps({'cmd': cmd, 'data': data})
        for client in filter(can_send_func, self.clients):
            try:
                client.write_message(body)
            except tornado.websocket.WebSocketClosedError:
                room_manager.del_client(self.room_id, client)

    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        asyncio.ensure_future(self.__on_danmaku(message))

    async def __on_danmaku(self, message: blivedm.DanmakuMessage):
        if message.uid == self.room_owner_uid:
            author_type = 3  # 主播
        elif message.admin:
            author_type = 2  # 房管
        elif message.privilege_type != 0:  # 1总督，2提督，3舰长
            author_type = 1  # 舰队
        else:
            author_type = 0

        if message.dm_type == 1:
            content_type = ContentType.EMOTICON
            content_type_params = make_emoticon_params(
                message.emoticon_options_dict['url'],
            )
        else:
            content_type = ContentType.TEXT
            content_type_params = None

        need_translate = self._need_translate(message.msg)
        if need_translate:
            translation = models.translate.get_translation_from_cache(message.msg)
            if translation is None:
                # 没有缓存，需要后面异步翻译后通知
                translation = ''
            else:
                need_translate = False
        else:
            translation = ''

        id_ = uuid.uuid4().hex
        # 为了节省带宽用list而不是dict
        self.send_message(Command.ADD_TEXT, make_text_message(
            avatar_url=await models.avatar.get_avatar_url(message.uid),
            timestamp=int(message.timestamp / 1000),
            author_name=message.uname,
            author_type=author_type,
            content=message.msg,
            privilege_type=message.privilege_type,
            is_gift_danmaku=message.msg_type,
            author_level=message.user_level,
            is_newbie=message.urank < 10000,
            is_mobile_verified=message.mobile_verify,
            medal_level=0 if message.medal_room_id != self.room_id else message.medal_level,
            id_=id_,
            translation=translation,
            content_type=content_type,
            content_type_params=content_type_params,
        ))

        if need_translate:
            await self._translate_and_response(message.msg, id_)

    async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
        avatar_url = models.avatar.process_avatar_url(message.face)
        models.avatar.update_avatar_cache(message.uid, avatar_url)
        if message.coin_type != 'gold':  # 丢人
            return
        id_ = uuid.uuid4().hex
        self.send_message(Command.ADD_GIFT, {
            'id': id_,
            'avatarUrl': avatar_url,
            'timestamp': message.timestamp,
            'authorName': message.uname,
            'totalCoin': message.total_coin,
            'giftName': message.gift_name,
            'num': message.num
        })

    async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
        asyncio.ensure_future(self.__on_buy_guard(message))

    async def __on_buy_guard(self, message: blivedm.GuardBuyMessage):
        id_ = uuid.uuid4().hex
        self.send_message(Command.ADD_MEMBER, {
            'id': id_,
            'avatarUrl': await models.avatar.get_avatar_url(message.uid),
            'timestamp': message.start_time,
            'authorName': message.username,
            'privilegeType': message.guard_level
        })

    async def _on_super_chat(self, client: blivedm.BLiveClient, message: blivedm.SuperChatMessage):
        avatar_url = models.avatar.process_avatar_url(message.face)
        models.avatar.update_avatar_cache(message.uid, avatar_url)

        need_translate = self._need_translate(message.message)
        if need_translate:
            translation = models.translate.get_translation_from_cache(message.message)
            if translation is None:
                # 没有缓存，需要后面异步翻译后通知
                translation = ''
            else:
                need_translate = False
        else:
            translation = ''

        id_ = str(message.id)
        self.send_message(Command.ADD_SUPER_CHAT, {
            'id': id_,
            'avatarUrl': avatar_url,
            'timestamp': message.start_time,
            'authorName': message.uname,
            'price': message.price,
            'content': message.message,
            'translation': translation
        })

        if need_translate:
            asyncio.ensure_future(self._translate_and_response(message.message, id_))

    async def _on_super_chat_delete(self, client: blivedm.BLiveClient, message: blivedm.SuperChatDeleteMessage):
        self.send_message(Command.ADD_SUPER_CHAT, {
            'ids': list(map(str, message.ids))
        })

    def _need_translate(self, text):
        cfg = config.get_config()
        return (
            cfg.enable_translate
            and (not cfg.allow_translate_rooms or self.room_id in cfg.allow_translate_rooms)
            and self.auto_translate_count > 0
            and models.translate.need_translate(text)
        )

    async def _translate_and_response(self, text, msg_id):
        translation = await models.translate.translate(text)
        if translation is None:
            return
        self.send_message_if(
            lambda client: client.auto_translate,
            Command.UPDATE_TRANSLATION, make_translation_message(
                msg_id,
                translation
            )
        )


def make_text_message(avatar_url, timestamp, author_name, author_type, content, privilege_type,
                      is_gift_danmaku, author_level, is_newbie, is_mobile_verified, medal_level,
                      id_, translation, content_type, content_type_params):
    return [
        # 0: avatarUrl
        avatar_url,
        # 1: timestamp
        timestamp,
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
        id_,
        # 12: translation
        translation,
        # 13: contentType
        content_type,
        # 14: contentTypeParams
        content_type_params if content_type_params is not None else [],
    ]


def make_emoticon_params(url):
    return [
        # 0: url
        url,
    ]


def make_translation_message(msg_id, translation):
    return [
        # 0: id
        msg_id,
        # 1: translation
        translation,
    ]


class RoomManager:
    def __init__(self):
        self._rooms: Dict[int, Room] = {}

    async def add_client(self, room_id, client: 'ChatHandler'):
        if room_id not in self._rooms:
            if not await self._add_room(room_id):
                client.close()
                return
        room = self._rooms.get(room_id, None)
        if room is None:
            return

        room.clients.append(client)
        logger.info('%d clients in room %s', len(room.clients), room_id)
        if client.auto_translate:
            room.auto_translate_count += 1

        await client.on_join_room()

    def del_client(self, room_id, client: 'ChatHandler'):
        room = self._rooms.get(room_id, None)
        if room is None:
            return

        try:
            room.clients.remove(client)
        except ValueError:
            # _add_room未完成，没有执行到room.clients.append
            pass
        else:
            logger.info('%d clients in room %s', len(room.clients), room_id)
            if client.auto_translate:
                room.auto_translate_count = max(0, room.auto_translate_count - 1)

        if not room.clients:
            self._del_room(room_id)

    async def _add_room(self, room_id):
        if room_id in self._rooms:
            return True
        logger.info('Creating room %d', room_id)
        self._rooms[room_id] = room = Room(room_id)
        if await room.init_room():
            room.start()
            logger.info('%d rooms', len(self._rooms))
            return True
        else:
            self._del_room(room_id)
            return False

    def _del_room(self, room_id):
        room = self._rooms.get(room_id, None)
        if room is None:
            return
        logger.info('Removing room %d', room_id)
        for client in room.clients:
            client.close()
        asyncio.ensure_future(room.stop_and_close())
        self._rooms.pop(room_id, None)
        logger.info('%d rooms', len(self._rooms))


# noinspection PyAbstractClass
class ChatHandler(tornado.websocket.WebSocketHandler):
    HEARTBEAT_INTERVAL = 10
    RECEIVE_TIMEOUT = HEARTBEAT_INTERVAL + 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._heartbeat_timer_handle = None
        self._receive_timeout_timer_handle = None

        self.room_id = None
        self.auto_translate = False

    def open(self):
        logger.info('Websocket connected %s', self.request.remote_ip)
        self._heartbeat_timer_handle = asyncio.get_event_loop().call_later(
            self.HEARTBEAT_INTERVAL, self._on_send_heartbeat
        )
        self._refresh_receive_timeout_timer()

    def _on_send_heartbeat(self):
        self.send_message(Command.HEARTBEAT, {})
        self._heartbeat_timer_handle = asyncio.get_event_loop().call_later(
            self.HEARTBEAT_INTERVAL, self._on_send_heartbeat
        )

    def _refresh_receive_timeout_timer(self):
        if self._receive_timeout_timer_handle is not None:
            self._receive_timeout_timer_handle.cancel()
        self._receive_timeout_timer_handle = asyncio.get_event_loop().call_later(
            self.RECEIVE_TIMEOUT, self._on_receive_timeout
        )

    def _on_receive_timeout(self):
        logger.warning('Client %s timed out', self.request.remote_ip)
        self._receive_timeout_timer_handle = None
        self.close()

    def on_close(self):
        logger.info('Websocket disconnected %s room: %s', self.request.remote_ip, str(self.room_id))
        if self.has_joined_room:
            room_manager.del_client(self.room_id, self)
        if self._heartbeat_timer_handle is not None:
            self._heartbeat_timer_handle.cancel()
            self._heartbeat_timer_handle = None
        if self._receive_timeout_timer_handle is not None:
            self._receive_timeout_timer_handle.cancel()
            self._receive_timeout_timer_handle = None

    def on_message(self, message):
        try:
            # 超时没有加入房间也断开
            if self.has_joined_room:
                self._refresh_receive_timeout_timer()

            body = json.loads(message)
            cmd = body['cmd']
            if cmd == Command.HEARTBEAT:
                pass
            elif cmd == Command.JOIN_ROOM:
                if self.has_joined_room:
                    return
                self._refresh_receive_timeout_timer()

                self.room_id = int(body['data']['roomId'])
                logger.info('Client %s is joining room %d', self.request.remote_ip, self.room_id)
                try:
                    cfg = body['data']['config']
                    self.auto_translate = cfg['autoTranslate']
                except KeyError:
                    pass

                asyncio.ensure_future(room_manager.add_client(self.room_id, self))
            else:
                logger.warning('Unknown cmd, client: %s, cmd: %d, body: %s', self.request.remote_ip, cmd, body)
        except Exception:
            logger.exception('on_message error, client: %s, message: %s', self.request.remote_ip, message)

    # 跨域测试用
    def check_origin(self, origin):
        if self.application.settings['debug']:
            return True
        return super().check_origin(origin)

    @property
    def has_joined_room(self):
        return self.room_id is not None

    def send_message(self, cmd, data):
        body = json.dumps({'cmd': cmd, 'data': data})
        try:
            self.write_message(body)
        except tornado.websocket.WebSocketClosedError:
            self.close()

    async def on_join_room(self):
        if self.application.settings['debug']:
            await self.send_test_message()

        # 不允许自动翻译的提示
        if self.auto_translate:
            cfg = config.get_config()
            if cfg.allow_translate_rooms and self.room_id not in cfg.allow_translate_rooms:
                self.send_message(Command.ADD_TEXT, make_text_message(
                    avatar_url=models.avatar.DEFAULT_AVATAR_URL,
                    timestamp=int(time.time()),
                    author_name='blivechat',
                    author_type=2,
                    content='Translation is not allowed in this room. Please download to use translation',
                    privilege_type=0,
                    is_gift_danmaku=False,
                    author_level=60,
                    is_newbie=False,
                    is_mobile_verified=True,
                    medal_level=0,
                    id_=uuid.uuid4().hex,
                    translation='',
                    content_type=ContentType.TEXT,
                    content_type_params=None,
                ))

    # 测试用
    async def send_test_message(self):
        base_data = {
            'avatarUrl': await models.avatar.get_avatar_url(300474),
            'timestamp': int(time.time()),
            'authorName': 'xfgryujk',
        }
        text_data = make_text_message(
            avatar_url=base_data['avatarUrl'],
            timestamp=base_data['timestamp'],
            author_name=base_data['authorName'],
            author_type=0,
            content='我能吞下玻璃而不伤身体',
            privilege_type=0,
            is_gift_danmaku=False,
            author_level=20,
            is_newbie=False,
            is_mobile_verified=True,
            medal_level=0,
            id_=uuid.uuid4().hex,
            translation='',
            content_type=ContentType.TEXT,
            content_type_params=None,
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
        self.send_message(Command.ADD_TEXT, text_data)
        text_data[2] = '主播'
        text_data[3] = 3
        text_data[4] = "I can eat glass, it doesn't hurt me."
        text_data[11] = uuid.uuid4().hex
        self.send_message(Command.ADD_TEXT, text_data)
        self.send_message(Command.ADD_MEMBER, member_data)
        self.send_message(Command.ADD_SUPER_CHAT, sc_data)
        sc_data['id'] = str(random.randint(1, 65535))
        sc_data['price'] = 100
        sc_data['content'] = '敏捷的棕色狐狸跳过了懒狗'
        self.send_message(Command.ADD_SUPER_CHAT, sc_data)
        # self.send_message(Command.DEL_SUPER_CHAT, {'ids': [sc_data['id']]})
        self.send_message(Command.ADD_GIFT, gift_data)
        gift_data['id'] = uuid.uuid4().hex
        gift_data['totalCoin'] = 1245000
        gift_data['giftName'] = '小电视飞船'
        self.send_message(Command.ADD_GIFT, gift_data)


# noinspection PyAbstractClass
class RoomInfoHandler(api.base.ApiHandler):
    _host_server_list_cache = blivedm_client.DEFAULT_DANMAKU_SERVER_LIST

    async def get(self):
        room_id = int(self.get_query_argument('roomId'))
        logger.info('Client %s is getting room info %d', self.request.remote_ip, room_id)
        room_id, owner_uid = await self._get_room_info(room_id)
        host_server_list = await self._get_server_host_list(room_id)
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
            async with _http_session.get(blivedm_client.ROOM_INIT_URL, params={'room_id': room_id}
                                         ) as res:
                if res.status != 200:
                    logger.warning('room %d _get_room_info failed: %d %s', room_id,
                                   res.status, res.reason)
                    return room_id, 0
                data = await res.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            logger.exception('room %d _get_room_info failed', room_id)
            return room_id, 0

        if data['code'] != 0:
            logger.warning('room %d _get_room_info failed: %s', room_id, data['message'])
            return room_id, 0

        room_info = data['data']['room_info']
        return room_info['room_id'], room_info['uid']

    @classmethod
    async def _get_server_host_list(cls, _room_id):
        return cls._host_server_list_cache

        # 连接其他host必须要key
        # try:
        #     async with _http_session.get(blivedm.DANMAKU_SERVER_CONF_URL, params={'id': room_id, 'type': 0}
        #                                  ) as res:
        #         if res.status != 200:
        #             logger.warning('room %d _get_server_host_list failed: %d %s', room_id,
        #                            res.status, res.reason)
        #             return cls._host_server_list_cache
        #         data = await res.json()
        # except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
        #     logger.exception('room %d _get_server_host_list failed', room_id)
        #     return cls._host_server_list_cache
        #
        # if data['code'] != 0:
        #     logger.warning('room %d _get_server_host_list failed: %s', room_id, data['message'])
        #     return cls._host_server_list_cache
        #
        # host_server_list = data['data']['host_list']
        # if not host_server_list:
        #     logger.warning('room %d _get_server_host_list failed: host_server_list is empty')
        #     return cls._host_server_list_cache
        #
        # cls._host_server_list_cache = host_server_list
        # return host_server_list


# noinspection PyAbstractClass
class AvatarHandler(api.base.ApiHandler):
    async def get(self):
        uid = int(self.get_query_argument('uid'))
        avatar_url = await models.avatar.get_avatar_url_or_none(uid)
        if avatar_url is None:
            avatar_url = models.avatar.DEFAULT_AVATAR_URL
            # 缓存3分钟
            self.set_header('Cache-Control', 'private, max-age=180')
        else:
            # 缓存1天
            self.set_header('Cache-Control', 'private, max-age=86400')
        self.write({
            'avatarUrl': avatar_url
        })
