# -*- coding: utf-8 -*-

import enum
import json
from typing import *

import tornado.websocket

import blivedm.blivedm as blivedm


class Command(enum.IntEnum):
    JOIN_ROOM = 0
    ADD_TEXT = 1
    ADD_GIFT = 2
    ADD_VIP = 3


class Room(blivedm.BLiveClient):
    def __init__(self, room_id):
        super().__init__(room_id)
        self.future = None
        self.clients: List['ChatHandler'] = []

    def start(self):
        self.future = self.run()

    def stop(self):
        if self.future is not None:
            self.future.cancel()

    def send_message(self, cmd, data):
        body = json.dumps({'cmd': cmd, 'data': data})
        for client in self.clients:
            client.write_message(body)

    async def _on_get_danmaku(self, content, user_name):
        # TODO
        data = {
            'content': content,
            'authorName': user_name
        }
        self.send_message(Command.ADD_TEXT, data)


class RoomManager:
    def __init__(self):
        self._rooms: Dict[int, Room] = {}

    def add_client(self, room_id, client):
        if room_id in self._rooms:
            room = self._rooms[room_id]
        else:
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
            room.stop()
            del self._rooms[room_id]


room_manager = RoomManager()


# noinspection PyAbstractClass
class ChatHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_id = None

    def on_message(self, message):
        if self.room_id is not None:
            return
        body = json.loads(message)
        if body['cmd'] == Command.JOIN_ROOM:
            room_id = body['data']['roomId']
            room_manager.add_client(room_id, self)

    def on_close(self):
        if self.room_id is not None:
            room_manager.del_client(self.room_id, self)

    # 测试用
    def check_origin(self, origin):
        return True
