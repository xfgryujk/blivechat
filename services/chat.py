# -*- coding: utf-8 -*-
import asyncio
import logging
import uuid
from typing import *

import api.chat
import blivedm.blivedm as blivedm
import config
import services.avatar
import services.translate
import utils.request

logger = logging.getLogger(__name__)

# 到B站的连接管理
_live_client_manager: Optional['LiveClientManager'] = None
# 到客户端的连接管理
client_room_manager: Optional['ClientRoomManager'] = None
# 直播消息处理器
_live_msg_handler: Optional['LiveMsgHandler'] = None


def init():
    global _live_client_manager, client_room_manager, _live_msg_handler
    _live_client_manager = LiveClientManager()
    client_room_manager = ClientRoomManager()
    _live_msg_handler = LiveMsgHandler()


class LiveClientManager:
    """管理到B站的连接"""
    def __init__(self):
        self._live_clients: Dict[int, LiveClient] = {}

    def add_live_client(self, room_id):
        if room_id in self._live_clients:
            return
        logger.info('room=%d creating live client', room_id)
        self._live_clients[room_id] = live_client = LiveClient(room_id)
        live_client.add_handler(_live_msg_handler)
        asyncio.ensure_future(self._init_live_client(live_client))
        logger.info('room=%d live client created, %d live clients', room_id, len(self._live_clients))

    async def _init_live_client(self, live_client: 'LiveClient'):
        if not await live_client.init_room():
            logger.warning('room=%d live client init failed', live_client.tmp_room_id)
            self.del_live_client(live_client.tmp_room_id)
            return
        logger.info('room=%d (%d) live client init succeeded', live_client.tmp_room_id, live_client.room_id)
        live_client.start()

    def del_live_client(self, room_id):
        live_client = self._live_clients.pop(room_id, None)
        if live_client is None:
            return
        logger.info('room=%d removing live client', room_id)
        live_client.remove_handler(_live_msg_handler)
        asyncio.ensure_future(live_client.stop_and_close())
        logger.info('room=%d live client removed, %d live clients', room_id, len(self._live_clients))

        client_room_manager.del_room(room_id)


class LiveClient(blivedm.BLiveClient):
    HEARTBEAT_INTERVAL = 10

    def __init__(self, room_id):
        super().__init__(room_id, session=utils.request.http_session, heartbeat_interval=self.HEARTBEAT_INTERVAL)

    @property
    def tmp_room_id(self):
        """初始化参数传入的房间ID，room_id可能改变，这个不会变"""
        return self._tmp_room_id

    async def init_room(self):
        await super().init_room()
        return True


class ClientRoomManager:
    """管理到客户端的连接"""
    # 房间没有客户端后延迟多久删除房间，不立即删除防止短时间后重连
    DELAY_DEL_ROOM_TIMEOUT = 10

    def __init__(self):
        self._rooms: Dict[int, ClientRoom] = {}
        # room_id -> timer_handle
        self._delay_del_timer_handles: Dict[int, asyncio.TimerHandle] = {}

    def add_client(self, room_id, client: 'api.chat.ChatHandler'):
        room = self._get_or_add_room(room_id)
        room.add_client(client)

        self._clear_delay_del_timer(room_id)

    def del_client(self, room_id, client: 'api.chat.ChatHandler'):
        room = self.get_room(room_id)
        if room is None:
            return
        room.del_client(client)

        if room.client_count == 0:
            self.delay_del_room(room_id, self.DELAY_DEL_ROOM_TIMEOUT)

    def get_room(self, room_id):
        return self._rooms.get(room_id, None)

    def _get_or_add_room(self, room_id):
        room = self._rooms.get(room_id, None)
        if room is None:
            logger.info('room=%d creating client room', room_id)
            self._rooms[room_id] = room = ClientRoom(room_id)
            logger.info('room=%d client room created, %d client rooms', room_id, len(self._rooms))

            _live_client_manager.add_live_client(room_id)
        return room

    def del_room(self, room_id):
        self._clear_delay_del_timer(room_id)

        room = self._rooms.pop(room_id, None)
        if room is None:
            return
        logger.info('room=%d removing client room', room_id)
        room.clear_clients()
        logger.info('room=%d client room removed, %d client rooms', room_id, len(self._rooms))

        _live_client_manager.del_live_client(room_id)

    def delay_del_room(self, room_id, timeout):
        self._clear_delay_del_timer(room_id)
        self._delay_del_timer_handles[room_id] = asyncio.get_event_loop().call_later(
            timeout, self._on_delay_del_room, room_id
        )

    def _clear_delay_del_timer(self, room_id):
        timer_handle = self._delay_del_timer_handles.pop(room_id, None)
        if timer_handle is not None:
            timer_handle.cancel()

    def _on_delay_del_room(self, room_id):
        self._delay_del_timer_handles.pop(room_id, None)
        self.del_room(room_id)


class ClientRoom:
    def __init__(self, room_id):
        self._room_id = room_id
        self._clients: List[api.chat.ChatHandler] = []
        self._auto_translate_count = 0

    @property
    def room_id(self):
        return self._room_id

    @property
    def client_count(self):
        return len(self._clients)

    @property
    def need_translate(self):
        return self._auto_translate_count > 0

    def add_client(self, client: 'api.chat.ChatHandler'):
        logger.info('room=%d addding client %s', self._room_id, client.request.remote_ip)
        self._clients.append(client)
        if client.auto_translate:
            self._auto_translate_count += 1
        logger.info('room=%d added client %s, %d clients', self._room_id, client.request.remote_ip,
                    self.client_count)

    def del_client(self, client: 'api.chat.ChatHandler'):
        client.close()
        try:
            self._clients.remove(client)
        except ValueError:
            return
        if client.auto_translate:
            self._auto_translate_count -= 1
        logger.info('room=%d removed client %s, %d clients', self._room_id, client.request.remote_ip,
                    self.client_count)

    def clear_clients(self):
        logger.info('room=%d clearing %d clients', self._room_id, self.client_count)
        for client in self._clients:
            client.close()
        self._clients.clear()
        self._auto_translate_count = 0

    def send_cmd_data(self, cmd, data):
        body = api.chat.make_message_body(cmd, data)
        for client in self._clients:
            client.send_body_no_raise(body)

    def send_cmd_data_if(self, filterer: Callable[['api.chat.ChatHandler'], bool], cmd, data):
        body = api.chat.make_message_body(cmd, data)
        for client in filter(filterer, self._clients):
            client.send_body_no_raise(body)


class LiveMsgHandler(blivedm.BaseHandler):
    # 重新定义XXX_callback是为了减少对字段名的依赖，防止B站改字段名
    def __danmu_msg_callback(self, client: LiveClient, command: dict):
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

    def __send_gift_callback(self, client: LiveClient, command: dict):
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

    def __guard_buy_callback(self, client: LiveClient, command: dict):
        data = command['data']
        message = blivedm.GuardBuyMessage(
            uid=data['uid'],
            username=data['username'],
            guard_level=data['guard_level'],
            start_time=data['start_time'],
        )
        return self._on_buy_guard(client, message)

    def __super_chat_message_callback(self, client: LiveClient, command: dict):
        data = command['data']
        message = blivedm.SuperChatMessage(
            price=data['price'],
            message=data['message'],
            start_time=data['start_time'],
            id=data['id'],
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

    async def _on_danmaku(self, client: LiveClient, message: blivedm.DanmakuMessage):
        asyncio.ensure_future(self.__on_danmaku(client, message))

    async def __on_danmaku(self, client: LiveClient, message: blivedm.DanmakuMessage):
        # 先异步调用再获取房间，因为返回时房间可能已经不存在了
        avatar_url = await services.avatar.get_avatar_url(message.uid)

        room = client_room_manager.get_room(client.tmp_room_id)
        if room is None:
            return

        if message.uid == client.room_owner_uid:
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

        need_translate = self._need_translate(message.msg, room)
        if need_translate:
            translation = services.translate.get_translation_from_cache(message.msg)
            if translation is None:
                # 没有缓存，需要后面异步翻译后通知
                translation = ''
            else:
                need_translate = False
        else:
            translation = ''

        msg_id = uuid.uuid4().hex
        room.send_cmd_data(api.chat.Command.ADD_TEXT, api.chat.make_text_message_data(
            avatar_url=avatar_url,
            timestamp=int(message.timestamp / 1000),
            author_name=message.uname,
            author_type=author_type,
            content=message.msg,
            privilege_type=message.privilege_type,
            is_gift_danmaku=bool(message.msg_type),
            author_level=message.user_level,
            is_newbie=message.urank < 10000,
            is_mobile_verified=bool(message.mobile_verify),
            medal_level=0 if message.medal_room_id != client.room_id else message.medal_level,
            id_=msg_id,
            translation=translation,
            content_type=content_type,
            content_type_params=content_type_params,
        ))

        if need_translate:
            await self._translate_and_response(message.msg, room.room_id, msg_id)

    async def _on_gift(self, client: LiveClient, message: blivedm.GiftMessage):
        avatar_url = services.avatar.process_avatar_url(message.face)
        # 服务器白给的头像URL，直接缓存
        services.avatar.update_avatar_cache(message.uid, avatar_url)

        # 丢人
        if message.coin_type != 'gold':
            return

        room = client_room_manager.get_room(client.tmp_room_id)
        if room is None:
            return

        room.send_cmd_data(api.chat.Command.ADD_GIFT, {
            'id': uuid.uuid4().hex,
            'avatarUrl': avatar_url,
            'timestamp': message.timestamp,
            'authorName': message.uname,
            'totalCoin': message.total_coin,
            'giftName': message.gift_name,
            'num': message.num
        })

    async def _on_buy_guard(self, client: LiveClient, message: blivedm.GuardBuyMessage):
        asyncio.ensure_future(self.__on_buy_guard(client, message))

    @staticmethod
    async def __on_buy_guard(client: LiveClient, message: blivedm.GuardBuyMessage):
        # 先异步调用再获取房间，因为返回时房间可能已经不存在了
        avatar_url = await services.avatar.get_avatar_url(message.uid)

        room = client_room_manager.get_room(client.tmp_room_id)
        if room is None:
            return

        room.send_cmd_data(api.chat.Command.ADD_MEMBER, {
            'id': uuid.uuid4().hex,
            'avatarUrl': avatar_url,
            'timestamp': message.start_time,
            'authorName': message.username,
            'privilegeType': message.guard_level
        })

    async def _on_super_chat(self, client: LiveClient, message: blivedm.SuperChatMessage):
        avatar_url = services.avatar.process_avatar_url(message.face)
        # 服务器白给的头像URL，直接缓存
        services.avatar.update_avatar_cache(message.uid, avatar_url)

        room = client_room_manager.get_room(client.tmp_room_id)
        if room is None:
            return

        need_translate = self._need_translate(message.message, room)
        if need_translate:
            translation = services.translate.get_translation_from_cache(message.message)
            if translation is None:
                # 没有缓存，需要后面异步翻译后通知
                translation = ''
            else:
                need_translate = False
        else:
            translation = ''

        msg_id = str(message.id)
        room.send_cmd_data(api.chat.Command.ADD_SUPER_CHAT, {
            'id': msg_id,
            'avatarUrl': avatar_url,
            'timestamp': message.start_time,
            'authorName': message.uname,
            'price': message.price,
            'content': message.message,
            'translation': translation
        })

        if need_translate:
            asyncio.ensure_future(self._translate_and_response(message.message, room.room_id, msg_id))

    async def _on_super_chat_delete(self, client: LiveClient, message: blivedm.SuperChatDeleteMessage):
        room = client_room_manager.get_room(client.tmp_room_id)
        if room is None:
            return

        room.send_cmd_data(api.chat.Command.DEL_SUPER_CHAT, {
            'ids': list(map(str, message.ids))
        })

    @staticmethod
    def _need_translate(text, room: ClientRoom):
        cfg = config.get_config()
        return (
            cfg.enable_translate
            and room.need_translate
            and (not cfg.allow_translate_rooms or room.room_id in cfg.allow_translate_rooms)
            and services.translate.need_translate(text)
        )

    @staticmethod
    async def _translate_and_response(text, room_id, msg_id):
        translation = await services.translate.translate(text)
        if translation is None:
            return

        room = client_room_manager.get_room(room_id)
        if room is None:
            return

        room.send_cmd_data_if(
            lambda client: client.auto_translate,
            api.chat.Command.UPDATE_TRANSLATION,
            api.chat.make_translation_message_data(
                msg_id,
                translation
            )
        )
