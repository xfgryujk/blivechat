# -*- coding: utf-8 -*-

import asyncio
import enum
import json
import logging
import time
from typing import *

import aiohttp
import tornado.websocket

import blivedm.blivedm as blivedm
import models.avatar

logger = logging.getLogger(__name__)


class Command(enum.IntEnum):
    HEARTBEAT = 0
    JOIN_ROOM = 1
    ADD_TEXT = 2
    ADD_GIFT = 3
    ADD_MEMBER = 4
    ADD_SUPER_CHAT = 5
    DEL_SUPER_CHAT = 6


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
                pass

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
        self.send_message(Command.ADD_TEXT, {
            'avatarUrl': await models.avatar.get_avatar_url(danmaku.uid),
            'timestamp': danmaku.timestamp,
            'authorName': danmaku.uname,
            'authorType': author_type,
            'content': danmaku.msg,
            'privilegeType': danmaku.privilege_type,
            'isGiftDanmaku': bool(danmaku.msg_type),
            'authorLevel': danmaku.user_level,
            'isNewbie': danmaku.urank < 10000,
            'isMobileVerified': bool(danmaku.mobile_verify),
            'medalLevel': 0 if danmaku.room_id != self.room_id else danmaku.medal_level
        })

    async def _on_receive_gift(self, gift: blivedm.GiftMessage):
        avatar_url = gift.face.replace('http:', '').replace('https:', '')
        models.avatar.update_avatar_cache(gift.uid, avatar_url)
        if gift.coin_type != 'gold':  # 丢人
            return
        self.send_message(Command.ADD_GIFT, {
            'avatarUrl': avatar_url,
            'timestamp': gift.timestamp,
            'authorName': gift.uname,
            'giftName': gift.gift_name,
            'giftNum': gift.num,
            'totalCoin': gift.total_coin
        })

    async def _on_buy_guard(self, message: blivedm.GuardBuyMessage):
        asyncio.ensure_future(self.__on_buy_guard(message))

    async def __on_buy_guard(self, message: blivedm.GuardBuyMessage):
        self.send_message(Command.ADD_MEMBER, {
            'avatarUrl':  await models.avatar.get_avatar_url(message.uid),
            'timestamp': message.start_time,
            'authorName': message.username
        })

    async def _on_super_chat(self, message: blivedm.SuperChatMessage):
        avatar_url = message.face.replace('http:', '').replace('https:', '')
        models.avatar.update_avatar_cache(message.uid, avatar_url)
        self.send_message(Command.ADD_SUPER_CHAT, {
            'avatarUrl': avatar_url,
            'timestamp': message.start_time,
            'authorName': message.uname,
            'price': message.price,
            'content': message.message,
            'id': message.id
        })

    async def _on_super_chat_delete(self, message: blivedm.SuperChatDeleteMessage):
        self.send_message(Command.ADD_SUPER_CHAT, {
            'ids':  message.ids
        })


class RoomManager:
    def __init__(self):
        self._rooms: Dict[int, Room] = {}

    async def add_client(self, room_id, client: 'ChatHandler'):
        if room_id not in self._rooms:
            if not await self._add_room(room_id):
                client.close()
                return
        room = self._rooms[room_id]
        room.clients.append(client)
        logger.info('%d clients in room %s', len(room.clients), room_id)

        if client.application.settings['debug']:
            client.send_test_message()

    def del_client(self, room_id, client: 'ChatHandler'):
        if room_id not in self._rooms:
            return
        room = self._rooms[room_id]
        room.clients.remove(client)
        logger.info('%d clients in room %s', len(room.clients), room_id)
        if not room.clients:
            self._del_room(room_id)

    async def _add_room(self, room_id):
        if room_id in self._rooms:
            return True
        logger.info('Creating room %d', room_id)
        room = Room(room_id)
        self._rooms[room_id] = room
        if await room.init_room():
            room.start()
            return True
        else:
            self._del_room(room_id)
            return False

    def _del_room(self, room_id):
        if room_id not in self._rooms:
            return
        logger.info('Removing room %d', room_id)
        room = self._rooms[room_id]
        for client in room.clients:
            client.close()
        room.stop_and_close()
        del self._rooms[room_id]


# noinspection PyAbstractClass
class ChatHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_id = None

    def open(self):
        logger.info('Websocket connected %s', self.request.remote_ip)

    def on_message(self, message):
        body = json.loads(message)
        cmd = body['cmd']
        if cmd == Command.HEARTBEAT:
            pass
        elif cmd == Command.JOIN_ROOM:
            if self.room_id is not None:
                return
            self.room_id = int(body['data']['roomId'])
            logger.info('Client %s is joining room %d', self.request.remote_ip, self.room_id)
            asyncio.ensure_future(room_manager.add_client(self.room_id, self))
        else:
            logger.warning('Unknown cmd: %s body: %s', cmd, body)

    def on_close(self):
        logger.info('Websocket disconnected %s room: %s', self.request.remote_ip, str(self.room_id))
        if self.room_id is not None:
            room_manager.del_client(self.room_id, self)

    # 跨域测试用
    def check_origin(self, origin):
        if self.application.settings['debug']:
            return True
        return super().check_origin(origin)

    # 测试用
    def send_test_message(self):
        base_data = {
            'avatarUrl':  '//i0.hdslb.com/bfs/face/29b6be8aa611e70a3d3ac219cdaf5e72b604f2de.jpg@48w_48h',
            'timestamp':  time.time(),
            'authorName': 'xfgryujk',
        }
        text_data = {
            **base_data,
            'authorType':       0,
            'content':          '我能吞下玻璃而不伤身体',
            'privilegeType':    0,
            'isGiftDanmaku':    False,
            'authorLevel':      20,
            'isNewbie':         False,
            'isMobileVerified': True
        }
        member_data = base_data
        gift_data = {
            **base_data,
            'giftName':  '摩天大楼',
            'giftNum':   1,
            'totalCoin': 450000
        }
        sc_data = {
            **base_data,
            'price':   30,
            'content': 'The quick brown fox jumps over the lazy dog',
            'id':      1
        }
        self.send_message(Command.ADD_TEXT, text_data)
        text_data['authorName'] = '主播'
        text_data['authorType'] = 3
        text_data['content'] = "I can eat glass, it doesn't hurt me."
        self.send_message(Command.ADD_TEXT, text_data)
        self.send_message(Command.ADD_MEMBER, member_data)
        self.send_message(Command.ADD_SUPER_CHAT, sc_data)
        sc_data['price'] = 100
        sc_data['content'] = '敏捷的棕色狐狸跳过了懒狗'
        sc_data['id'] = 2
        self.send_message(Command.ADD_SUPER_CHAT, sc_data)
        # self.send_message(Command.DEL_SUPER_CHAT, {'ids': [1, 2]})
        self.send_message(Command.ADD_GIFT, gift_data)
        gift_data['giftName'] = '小电视飞船'
        gift_data['totalCoin'] = 1245000
        self.send_message(Command.ADD_GIFT, gift_data)

    def send_message(self, cmd, data):
        body = json.dumps({'cmd': cmd, 'data': data})
        try:
            self.write_message(body)
        except tornado.websocket.WebSocketClosedError:
            pass
