# -*- coding: utf-8 -*-
import asyncio
import json
import logging
import uuid
from typing import *

import tornado.websocket

import api.chat
import blivedm.blivedm as blivedm
import config
import services.avatar
import services.translate
import utils.request

logger = logging.getLogger(__name__)

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
        super().__init__(room_id, session=utils.request.http_session, heartbeat_interval=self.HEARTBEAT_INTERVAL)
        self.add_handler(self)
        self.clients: List[api.chat.ChatHandler] = []
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

    def send_message_if(self, can_send_func: Callable[['api.chat.ChatHandler'], bool], cmd, data):
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
            content_type = api.chat.ContentType.EMOTICON
            content_type_params = api.chat.make_emoticon_params(
                message.emoticon_options_dict['url'],
            )
        else:
            content_type = api.chat.ContentType.TEXT
            content_type_params = None

        need_translate = self._need_translate(message.msg)
        if need_translate:
            translation = services.translate.get_translation_from_cache(message.msg)
            if translation is None:
                # 没有缓存，需要后面异步翻译后通知
                translation = ''
            else:
                need_translate = False
        else:
            translation = ''

        id_ = uuid.uuid4().hex
        # 为了节省带宽用list而不是dict
        self.send_message(api.chat.Command.ADD_TEXT, api.chat.make_text_message(
            avatar_url=await services.avatar.get_avatar_url(message.uid),
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
        avatar_url = services.avatar.process_avatar_url(message.face)
        services.avatar.update_avatar_cache(message.uid, avatar_url)
        if message.coin_type != 'gold':  # 丢人
            return
        id_ = uuid.uuid4().hex
        self.send_message(api.chat.Command.ADD_GIFT, {
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
        self.send_message(api.chat.Command.ADD_MEMBER, {
            'id': id_,
            'avatarUrl': await services.avatar.get_avatar_url(message.uid),
            'timestamp': message.start_time,
            'authorName': message.username,
            'privilegeType': message.guard_level
        })

    async def _on_super_chat(self, client: blivedm.BLiveClient, message: blivedm.SuperChatMessage):
        avatar_url = services.avatar.process_avatar_url(message.face)
        services.avatar.update_avatar_cache(message.uid, avatar_url)

        need_translate = self._need_translate(message.message)
        if need_translate:
            translation = services.translate.get_translation_from_cache(message.message)
            if translation is None:
                # 没有缓存，需要后面异步翻译后通知
                translation = ''
            else:
                need_translate = False
        else:
            translation = ''

        id_ = str(message.id)
        self.send_message(api.chat.Command.ADD_SUPER_CHAT, {
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
        self.send_message(api.chat.Command.ADD_SUPER_CHAT, {
            'ids': list(map(str, message.ids))
        })

    def _need_translate(self, text):
        cfg = config.get_config()
        return (
                cfg.enable_translate
                and (not cfg.allow_translate_rooms or self.room_id in cfg.allow_translate_rooms)
                and self.auto_translate_count > 0
                and services.translate.need_translate(text)
        )

    async def _translate_and_response(self, text, msg_id):
        translation = await services.translate.translate(text)
        if translation is None:
            return
        self.send_message_if(
            lambda client: client.auto_translate,
            api.chat.Command.UPDATE_TRANSLATION,
            api.chat.make_translation_message(
                msg_id,
                translation
            )
        )


class RoomManager:
    def __init__(self):
        self._rooms: Dict[int, Room] = {}

    async def add_client(self, room_id, client: 'api.chat.ChatHandler'):
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

    def del_client(self, room_id, client: 'api.chat.ChatHandler'):
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
