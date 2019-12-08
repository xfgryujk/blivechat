# -*- coding: utf-8 -*-

import asyncio
import datetime
import enum
import json
import logging
import time
from typing import *

import aiohttp
import tornado.websocket

import blivedm.blivedm as blivedm

logger = logging.getLogger(__name__)


class Command(enum.IntEnum):
    HEARTBEAT = 0
    JOIN_ROOM = 1
    ADD_TEXT = 2
    ADD_GIFT = 3
    ADD_MEMBER = 4
    ADD_SUPER_CHAT = 5
    DEL_SUPER_CHAT = 6


DEFAULT_AVATAR_URL = '//static.hdslb.com/images/member/noface.gif'

_http_session = aiohttp.ClientSession()
_avatar_url_cache: Dict[int, str] = {}
_last_fetch_avatar_time = datetime.datetime.now()
_last_avatar_failed_time = None
_uids_to_fetch_avatar = asyncio.Queue(15)


async def get_avatar_url(user_id):
    if user_id in _avatar_url_cache:
        return _avatar_url_cache[user_id]

    global _last_avatar_failed_time, _last_fetch_avatar_time
    cur_time = datetime.datetime.now()
    # 防止获取头像频率太高被ban
    if (cur_time - _last_fetch_avatar_time).total_seconds() < 0.2:
        # 由_fetch_avatar_loop过一段时间再获取并缓存
        try:
            _uids_to_fetch_avatar.put_nowait(user_id)
        except asyncio.QueueFull:
            pass
        return DEFAULT_AVATAR_URL

    if _last_avatar_failed_time is not None:
        if (cur_time - _last_avatar_failed_time).total_seconds() < 3 * 60 + 3:
            # 3分钟以内被ban，解封大约要15分钟
            return DEFAULT_AVATAR_URL
        else:
            _last_avatar_failed_time = None

    _last_fetch_avatar_time = cur_time
    try:
        async with _http_session.get('https://api.bilibili.com/x/space/acc/info',
                                     params={'mid': user_id}) as r:
            if r.status != 200:  # 可能会被B站ban
                logger.warning('Failed to fetch avatar: status=%d %s uid=%d', r.status, r.reason, user_id)
                _last_avatar_failed_time = cur_time
                return DEFAULT_AVATAR_URL
            data = await r.json()
    except aiohttp.ClientConnectionError:
        return DEFAULT_AVATAR_URL
    url = data['data']['face'].replace('http:', '').replace('https:', '')
    if not url.endswith('noface.gif'):
        url += '@48w_48h'
    _avatar_url_cache[user_id] = url

    if len(_avatar_url_cache) > 50000:
        for _, key in zip(range(100), _avatar_url_cache):
            del _avatar_url_cache[key]

    return url


async def _fetch_avatar_loop():
    while True:
        try:
            user_id = await _uids_to_fetch_avatar.get()
            if user_id in _avatar_url_cache:
                continue
            # 延时长一些使实时弹幕有机会获取头像
            await asyncio.sleep(0.4 - (datetime.datetime.now() - _last_fetch_avatar_time).total_seconds())
            asyncio.ensure_future(get_avatar_url(user_id))
        except:
            pass


asyncio.ensure_future(_fetch_avatar_loop())


class Room(blivedm.BLiveClient):
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
            'avatarUrl': await get_avatar_url(danmaku.uid),
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
        if gift.coin_type != 'gold':  # 丢人
            return
        self.send_message(Command.ADD_GIFT, {
            'avatarUrl': gift.face.replace('http:', '').replace('https:', ''),
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
            'avatarUrl':  await get_avatar_url(message.uid),
            'timestamp': message.start_time,
            'authorName': message.username
        })

    async def _on_super_chat(self, message: blivedm.SuperChatMessage):
        self.send_message(Command.ADD_SUPER_CHAT, {
            'avatarUrl': message.face.replace('http:', '').replace('https:', ''),
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


room_manager = RoomManager()


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
