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
    JOIN_ROOM = 0
    ADD_TEXT = 1
    ADD_GIFT = 2
    ADD_MEMBER = 3


_http_session = aiohttp.ClientSession()
_avatar_url_cache: Dict[int, str] = {}
_last_avatar_failed_time = None


async def get_avatar_url(user_id):
    if user_id in _avatar_url_cache:
        return _avatar_url_cache[user_id]

    global _last_avatar_failed_time
    if _last_avatar_failed_time is not None:
        if (datetime.datetime.now() - _last_avatar_failed_time).seconds < 5 * 60:
            # 5分钟以内被ban
            return 'https://static.hdslb.com/images/member/noface.gif'
        else:
            _last_avatar_failed_time = None

    async with _http_session.get('https://api.bilibili.com/x/space/acc/info',
                                 params={'mid': user_id}) as r:
        if r.status != 200:  # 可能会被B站ban
            logger.warning('获取头像失败：status=%d %s uid=%d', r.status, r.reason, user_id)
            _last_avatar_failed_time = datetime.datetime.now()
            return 'https://static.hdslb.com/images/member/noface.gif'
        data = await r.json()
    url = data['data']['face']
    if not url.endswith('noface.gif'):
        url += '@48w_48h'
    _avatar_url_cache[user_id] = url

    if len(_avatar_url_cache) > 50000:
        for _, key in zip(range(100), _avatar_url_cache):
            del _avatar_url_cache[key]

    return url


class Room(blivedm.BLiveClient):
    def __init__(self, room_id):
        super().__init__(room_id, session=_http_session)
        self.clients: List['ChatHandler'] = []

    def stop_and_close(self):
        future = self.stop()
        future.add_done_callback(lambda _future: asyncio.ensure_future(self.close()))

    def send_message(self, cmd, data):
        body = json.dumps({'cmd': cmd, 'data': data})
        for client in self.clients:
            client.write_message(body)

    async def _on_receive_danmaku(self, danmaku: blivedm.DanmakuMessage):
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
            'isMobileVerified': bool(danmaku.mobile_verify)
        })

    async def _on_receive_gift(self, gift: blivedm.GiftMessage):
        if gift.coin_type != 'gold':  # 丢人
            return
        self.send_message(Command.ADD_GIFT, {
            'avatarUrl': await get_avatar_url(gift.uid),
            'timestamp': gift.timestamp,
            'authorName': gift.uname,
            'giftName': gift.gift_name,
            'giftNum': gift.num,
            'totalCoin': gift.total_coin
        })

    async def _on_buy_guard(self, message: blivedm.GuardBuyMessage):
        self.send_message(Command.ADD_MEMBER, {
            'avatarUrl':  await get_avatar_url(message.uid),
            'timestamp': message.start_time,
            'authorName': message.username
        })


class RoomManager:
    def __init__(self):
        self._rooms: Dict[int, Room] = {}

    def add_client(self, room_id, client: 'ChatHandler'):
        if room_id in self._rooms:
            room = self._rooms[room_id]
        else:
            logger.info('创建房间%d', room_id)
            room = Room(room_id)
            self._rooms[room_id] = room
            room.start()
        room.clients.append(client)

        if client.application.settings['debug']:
            self.__send_test_message(room)

    def del_client(self, room_id, client: 'ChatHandler'):
        if room_id not in self._rooms:
            return
        room = self._rooms[room_id]
        room.clients.remove(client)
        if not room.clients:
            logger.info('移除房间%d', room_id)
            room.stop_and_close()
            del self._rooms[room_id]

    # 测试用
    @staticmethod
    def __send_test_message(room):
        base_data = {
            'avatarUrl':  'https://i0.hdslb.com/bfs/face/29b6be8aa611e70a3d3ac219cdaf5e72b604f2de.jpg@48w_48h',
            'timestamp':  time.time(),
            'authorName': 'xfgryujk',
        }
        text_data = {
            **base_data,
            'authorType': 0,
            'content': '我能吞下玻璃而不伤身体',
            'privilegeType': 0,
            'isGiftDanmaku': False,
            'authorLevel': 20,
            'isNewbie': False,
            'isMobileVerified': True
        }
        vip_data = base_data
        gift_data = {
            **base_data,
            'giftName': '礼花',
            'giftNum': 1,
            'totalCoin': 28000
        }
        room.send_message(Command.ADD_TEXT, text_data)
        text_data['authorName'] = '主播'
        text_data['authorType'] = 3
        text_data['content'] = "I can eat glass, it doesn't hurt me."
        room.send_message(Command.ADD_TEXT, text_data)
        room.send_message(Command.ADD_MEMBER, vip_data)
        room.send_message(Command.ADD_GIFT, gift_data)
        gift_data['giftName'] = '节奏风暴'
        gift_data['totalCoin'] = 100000
        room.send_message(Command.ADD_GIFT, gift_data)
        gift_data['giftName'] = '摩天大楼'
        gift_data['totalCoin'] = 450000
        room.send_message(Command.ADD_GIFT, gift_data)
        gift_data['giftName'] = '小电视飞船'
        gift_data['totalCoin'] = 1245000
        room.send_message(Command.ADD_GIFT, gift_data)


room_manager = RoomManager()


# noinspection PyAbstractClass
class ChatHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_id = None

    def open(self):
        logger.info('Websocket连接 %s', self.request.remote_ip)

    def on_message(self, message):
        if self.room_id is not None:
            return
        body = json.loads(message)
        if body['cmd'] == Command.JOIN_ROOM:
            self.room_id = int(body['data']['roomId'])
            logger.info('客户端%s加入房间%d', self.request.remote_ip, self.room_id)
            room_manager.add_client(self.room_id, self)
        else:
            logger.warning('未知的命令: %s data: %s', body['cmd'], body['data'])

    def on_close(self):
        logger.info('Websocket断开 %s room: %s', self.request.remote_ip, self.room_id)
        if self.room_id is not None:
            room_manager.del_client(self.room_id, self)

    # 跨域测试用
    def check_origin(self, origin):
        if self.application.settings['debug']:
            return True
        return super().check_origin(origin)
