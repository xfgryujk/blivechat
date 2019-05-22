# -*- coding: utf-8 -*-

import asyncio
import enum
import json
import logging
from typing import *

import tornado.websocket

import blivedm.blivedm as blivedm

logger = logging.getLogger(__name__)


class Command(enum.IntEnum):
    JOIN_ROOM = 0
    ADD_TEXT = 1
    ADD_GIFT = 2
    ADD_VIP = 3


class Room(blivedm.BLiveClient):
    _COMMAND_HANDLERS = blivedm.BLiveClient._COMMAND_HANDLERS.copy()

    def __init__(self, room_id):
        super().__init__(room_id)
        self.future = None
        self.clients: List['ChatHandler'] = []

    def start(self):
        self.future = self.run()

    def stop(self):
        if self.future is not None:
            self.future.cancel()
        asyncio.ensure_future(self.close())

    def send_message(self, cmd, data):
        body = json.dumps({'cmd': cmd, 'data': data})
        for client in self.clients:
            client.write_message(body)

    async def __my_on_get_danmaku(self, command):
        user_id = command['info'][2][0]
        # TODO 获取头像
        data = {
            'avatarUrl': 'https://i0.hdslb.com/bfs/face/29b6be8aa611e70a3d3ac219cdaf5e72b604f2de.jpg@24w_24h.webp',
            'timestamp': command['info'][0][4],
            'content': command['info'][1],
            'authorName': command['info'][2][1]
        }
        self.send_message(Command.ADD_TEXT, data)

    _COMMAND_HANDLERS['SEND_GIFT'] = __my_on_get_danmaku


class RoomManager:
    def __init__(self):
        self._rooms: Dict[int, Room] = {}

    def add_client(self, room_id, client):
        if room_id in self._rooms:
            room = self._rooms[room_id]
        else:
            logger.info('创建房间%d', room_id)
            room = Room(room_id)
            self._rooms[room_id] = room
            room.start()
        room.clients.append(client)

    def del_client(self, room_id, client: 'ChatHandler'):
        if room_id not in self._rooms:
            return
        room = self._rooms[room_id]
        room.clients.remove(client)
        if not room.clients:
            logger.info('移除房间%d', room_id)
            room.stop()
            del self._rooms[room_id]


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

    # 测试用
    def check_origin(self, origin):
        return True
