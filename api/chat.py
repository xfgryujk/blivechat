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

import blivedm.blivedm as blivedm
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


_http_session = aiohttp.ClientSession()

room_manager: Optional['RoomManager'] = None


def init():
    global room_manager
    room_manager = RoomManager()


class Room(blivedm.BLiveClient):
    # 重新定义parse_XXX是为了减少对字段名的依赖，防止B站改字段名
    def __parse_danmaku(self, command):
        info = command['info']
        if info[3]:
            room_id = info[3][3]
            medal_level = info[3][0]
        else:
            room_id = medal_level = 0
        return self._on_receive_danmaku(blivedm.DanmakuMessage(
            None, None, None, info[0][4], None, None, info[0][9], None,
            info[1],
            info[2][0], info[2][1], info[2][2], None, None, info[2][5], info[2][6], None,
            medal_level, None, None, room_id, None, None,
            info[4][0], None, None,
            None, None,
            info[7]
        ))

    def __parse_gift(self, command):
        data = command['data']
        return self._on_receive_gift(blivedm.GiftMessage(
            data['giftName'], data['num'], data['uname'], data['face'], None,
            data['uid'], data['timestamp'], None, None,
            None, None, None, data['coin_type'], data['total_coin']
        ))

    def __parse_buy_guard(self, command):
        data = command['data']
        return self._on_buy_guard(blivedm.GuardBuyMessage(
            data['uid'], data['username'], None, None, None,
            None, None, data['start_time'], None
        ))

    def __parse_super_chat(self, command):
        data = command['data']
        return self._on_super_chat(blivedm.SuperChatMessage(
            data['price'], data['message'], None, data['start_time'],
            None, None, data['id'], None,
            None, data['uid'], data['user_info']['uname'],
            data['user_info']['face'], None,
            None, None,
            None, None, None,
            None
        ))

    _COMMAND_HANDLERS = {
        **blivedm.BLiveClient._COMMAND_HANDLERS,
        'DANMU_MSG': __parse_danmaku,
        'SEND_GIFT': __parse_gift,
        'GUARD_BUY': __parse_buy_guard,
        'SUPER_CHAT_MESSAGE': __parse_super_chat
    }

    def __init__(self, room_id):
        super().__init__(room_id, session=_http_session, heartbeat_interval=10)
        self.clients: List['ChatHandler'] = []
        self.auto_translate_count = 0

    def stop_and_close(self):
        if self.is_running:
            future = self.stop()
            future.add_done_callback(lambda _future: asyncio.ensure_future(self.close()))
        else:
            asyncio.ensure_future(self.close())

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

    async def _on_receive_danmaku(self, danmaku: blivedm.DanmakuMessage):
        asyncio.ensure_future(self.__on_receive_danmaku(danmaku))

    async def __on_receive_danmaku(self, danmaku: blivedm.DanmakuMessage):
        if danmaku.uid == self.room_owner_uid:
            author_type = 3  # 主播
        elif danmaku.admin:
            author_type = 2  # 房管
        elif danmaku.privilege_type != 0:  # 1总督，2提督，3舰长
            author_type = 1  # 舰队
        else:
            author_type = 0

        need_translate = self._need_translate(danmaku.msg)
        if need_translate:
            translation = models.translate.get_translation_from_cache(danmaku.msg)
            if translation is None:
                # 没有缓存，需要后面异步翻译后通知
                translation = ''
            else:
                need_translate = False
        else:
            translation = ''

        id_ = uuid.uuid4().hex
        # 为了节省带宽用list而不是dict
        self.send_message(Command.ADD_TEXT, [
            # 0: avatarUrl
            await models.avatar.get_avatar_url(danmaku.uid),
            # 1: timestamp
            int(danmaku.timestamp / 1000),
            # 2: authorName
            danmaku.uname,
            # 3: authorType
            author_type,
            # 4: content
            danmaku.msg,
            # 5: privilegeType
            danmaku.privilege_type,
            # 6: isGiftDanmaku
            1 if danmaku.msg_type else 0,
            # 7: authorLevel
            danmaku.user_level,
            # 8: isNewbie
            1 if danmaku.urank < 10000 else 0,
            # 9: isMobileVerified
            1 if danmaku.mobile_verify else 0,
            # 10: medalLevel
            0 if danmaku.room_id != self.room_id else danmaku.medal_level,
            # 11: id
            id_,
            # 12: translation
            translation
        ])

        if need_translate:
            await self._translate_and_response(danmaku.msg, id_)

    async def _on_receive_gift(self, gift: blivedm.GiftMessage):
        avatar_url = models.avatar.process_avatar_url(gift.face)
        models.avatar.update_avatar_cache(gift.uid, avatar_url)
        if gift.coin_type != 'gold':  # 丢人
            return
        id_ = uuid.uuid4().hex
        self.send_message(Command.ADD_GIFT, {
            'id': id_,
            'avatarUrl': avatar_url,
            'timestamp': gift.timestamp,
            'authorName': gift.uname,
            'totalCoin': gift.total_coin,
            'giftName': gift.gift_name,
            'num': gift.num
        })

    async def _on_buy_guard(self, message: blivedm.GuardBuyMessage):
        asyncio.ensure_future(self.__on_buy_guard(message))

    async def __on_buy_guard(self, message: blivedm.GuardBuyMessage):
        id_ = uuid.uuid4().hex
        self.send_message(Command.ADD_MEMBER, {
            'id': id_,
            'avatarUrl': await models.avatar.get_avatar_url(message.uid),
            'timestamp': message.start_time,
            'authorName': message.username
        })

    async def _on_super_chat(self, message: blivedm.SuperChatMessage):
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

    async def _on_super_chat_delete(self, message: blivedm.SuperChatDeleteMessage):
        self.send_message(Command.ADD_SUPER_CHAT, {
            'ids': list(map(str, message.ids))
        })

    def _need_translate(self, text):
        return (
            config.get_config().enable_translate
            and self.auto_translate_count > 0
            and models.translate.need_translate(text)
        )

    async def _translate_and_response(self, text, msg_id):
        translation = await models.translate.translate(text)
        if translation is None:
            return
        self.send_message_if(
            lambda client: client.auto_translate,
            Command.UPDATE_TRANSLATION,
            [
                # 0: id
                msg_id,
                # 1: translation
                translation
            ]
        )


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

        if client.application.settings['debug']:
            await client.send_test_message()

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
        room.stop_and_close()
        self._rooms.pop(room_id, None)
        logger.info('%d rooms', len(self._rooms))


# noinspection PyAbstractClass
class ChatHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._close_on_timeout_future = None
        self.room_id = None
        self.auto_translate = False

    def open(self):
        logger.info('Websocket connected %s', self.request.remote_ip)
        self._close_on_timeout_future = asyncio.ensure_future(self._close_on_timeout())

    async def _close_on_timeout(self):
        try:
            # 超过一定时间还没加入房间则断开
            await asyncio.sleep(10)
            logger.warning('Client %s joining room timed out', self.request.remote_ip)
            self.close()
        except (asyncio.CancelledError, tornado.websocket.WebSocketClosedError):
            pass

    def on_message(self, message):
        try:
            body = json.loads(message)
            cmd = body['cmd']
            if cmd == Command.HEARTBEAT:
                return
            elif cmd == Command.JOIN_ROOM:
                if self.has_joined_room:
                    return
                self.room_id = int(body['data']['roomId'])
                logger.info('Client %s is joining room %d', self.request.remote_ip, self.room_id)
                try:
                    cfg = body['data']['config']
                    self.auto_translate = cfg['autoTranslate']
                except KeyError:
                    pass

                asyncio.ensure_future(room_manager.add_client(self.room_id, self))
                self._close_on_timeout_future.cancel()
                self._close_on_timeout_future = None
            else:
                logger.warning('Unknown cmd, client: %s, cmd: %d, body: %s', self.request.remote_ip, cmd, body)
        except:
            logger.exception('on_message error, client: %s, message: %s', self.request.remote_ip, message)

    def on_close(self):
        logger.info('Websocket disconnected %s room: %s', self.request.remote_ip, str(self.room_id))
        if self.has_joined_room:
            room_manager.del_client(self.room_id, self)
        if self._close_on_timeout_future is not None:
            self._close_on_timeout_future.cancel()
            self._close_on_timeout_future = None

    # 跨域测试用
    def check_origin(self, origin):
        if self.application.settings['debug']:
            return True
        return super().check_origin(origin)

    # 测试用
    async def send_test_message(self):
        base_data = {
            'avatarUrl': await models.avatar.get_avatar_url(300474),
            'timestamp': int(time.time()),
            'authorName': 'xfgryujk',
        }
        text_data = [
            # 0: avatarUrl
            base_data['avatarUrl'],
            # 1: timestamp
            base_data['timestamp'],
            # 2: authorName
            base_data['authorName'],
            # 3: authorType
            0,
            # 4: content
            '我能吞下玻璃而不伤身体',
            # 5: privilegeType
            0,
            # 6: isGiftDanmaku
            0,
            # 7: authorLevel
            20,
            # 8: isNewbie
            0,
            # 9: isMobileVerified
            1,
            # 10: medalLevel
            0,
            # 11: id
            uuid.uuid4().hex,
            # 12: translation
            ''
        ]
        member_data = {
            **base_data,
            'id': uuid.uuid4().hex
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

    @property
    def has_joined_room(self):
        return self.room_id is not None

    def send_message(self, cmd, data):
        body = json.dumps({'cmd': cmd, 'data': data})
        try:
            self.write_message(body)
        except tornado.websocket.WebSocketClosedError:
            self.on_close()
