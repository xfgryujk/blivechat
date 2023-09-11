# -*- coding: utf-8 -*-
import asyncio
import enum
import logging
import uuid
from typing import *

import api.chat
import api.open_live as api_open_live
import blivedm.blivedm as blivedm
import blivedm.blivedm.models.open_live as dm_open_models
import blivedm.blivedm.models.web as dm_web_models
import config
import services.avatar
import services.translate
import utils.request

logger = logging.getLogger(__name__)


class RoomKeyType(enum.IntEnum):
    ROOM_ID = 1
    AUTH_CODE = 2


class RoomKey(NamedTuple):
    """内部用来标识一个房间，由客户端加入房间时传入"""
    type: RoomKeyType
    value: Union[int, str]

    def __str__(self):
        res = str(self.value)
        if self.type == RoomKeyType.AUTH_CODE:
            # 身份码要脱敏
            res = '***' + res[-3:]
        return res
    __repr__ = __str__


# 用于类型标注的类型别名
LiveClientType = Union['WebLiveClient', 'OpenLiveClient']

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


async def shut_down():
    if client_room_manager is not None:
        client_room_manager.shut_down()
    if _live_client_manager is not None:
        await _live_client_manager.shut_down()


class LiveClientManager:
    """管理到B站的连接"""
    def __init__(self):
        self._live_clients: Dict[RoomKey, LiveClientType] = {}
        self._close_client_futures: Set[asyncio.Future] = set()

    async def shut_down(self):
        while len(self._live_clients) != 0:
            room_key = next(iter(self._live_clients))
            self.del_live_client(room_key)

        await asyncio.gather(*self._close_client_futures, return_exceptions=True)

    def add_live_client(self, room_key: RoomKey):
        if room_key in self._live_clients:
            return

        logger.info('room=%s creating live client', room_key)

        self._live_clients[room_key] = live_client = self._create_live_client(room_key)
        live_client.set_handler(_live_msg_handler)
        # 直接启动吧，这里不用管init_room失败的情况，万一失败了会在on_client_stopped里删除掉这个客户端
        live_client.start()

        logger.info('room=%s live client created, %d live clients', room_key, len(self._live_clients))

    @staticmethod
    def _create_live_client(room_key: RoomKey):
        if room_key.type == RoomKeyType.ROOM_ID:
            return WebLiveClient(room_key)
        elif room_key.type == RoomKeyType.AUTH_CODE:
            return OpenLiveClient(room_key)
        raise ValueError(f'Unknown RoomKeyType={room_key.type}')

    def del_live_client(self, room_key: RoomKey):
        live_client = self._live_clients.pop(room_key, None)
        if live_client is None:
            return

        logger.info('room=%s removing live client', room_key)

        live_client.set_handler(None)
        future = asyncio.create_task(live_client.stop_and_close())
        self._close_client_futures.add(future)
        future.add_done_callback(lambda _future: self._close_client_futures.discard(future))

        logger.info('room=%s live client removed, %d live clients', room_key, len(self._live_clients))

        client_room_manager.del_room(room_key)


class WebLiveClient(blivedm.BLiveClient):
    HEARTBEAT_INTERVAL = 10

    def __init__(self, room_key: RoomKey):
        assert room_key.type == RoomKeyType.ROOM_ID
        super().__init__(
            room_key.value,
            session=utils.request.http_session,
            heartbeat_interval=self.HEARTBEAT_INTERVAL,
        )

    @property
    def room_key(self):
        return RoomKey(RoomKeyType.ROOM_ID, self.tmp_room_id)

    async def init_room(self):
        res = await super().init_room()
        if res:
            logger.info('room=%s live client init succeeded, room_id=%d', self.room_key, self.room_id)
        else:
            logger.info('room=%s live client init with a downgrade, room_id=%d', self.room_key, self.room_id)
        # 允许降级
        return True


class OpenLiveClient(blivedm.OpenLiveClient):
    HEARTBEAT_INTERVAL = 10

    def __init__(self, room_key: RoomKey):
        assert room_key.type == RoomKeyType.AUTH_CODE
        cfg = config.get_config()
        super().__init__(
            access_key_id=cfg.open_live_access_key_id,
            access_key_secret=cfg.open_live_access_key_secret,
            app_id=cfg.open_live_app_id,
            room_owner_auth_code=room_key.value,
            session=utils.request.http_session,
            heartbeat_interval=self.HEARTBEAT_INTERVAL,
        )

    @property
    def room_key(self):
        return RoomKey(RoomKeyType.AUTH_CODE, self.room_owner_auth_code)

    async def init_room(self):
        res = await super().init_room()
        if res:
            logger.info('room=%s live client init succeeded, room_id=%d', self.room_key, self.room_id)
        else:
            logger.info('room=%s live client init failed', self.room_key)
        return res

    async def _start_game(self):
        try:
            data = await api_open_live.request_open_live_or_common_server(
                api_open_live.START_GAME_OPEN_LIVE_URL,
                api_open_live.START_GAME_COMMON_SERVER_URL,
                {'code': self._room_owner_auth_code, 'app_id': self._app_id}
            )
        except api_open_live.TransportError:
            logger.error('_start_game() failed')
            return False
        except api_open_live.BusinessError:
            logger.warning('_start_game() failed')
            return False
        return self._parse_start_game(data['data'])

    async def _end_game(self):
        if self._game_id in (None, ''):
            return True

        try:
            await api_open_live.request_open_live_or_common_server(
                api_open_live.END_GAME_OPEN_LIVE_URL,
                api_open_live.END_GAME_COMMON_SERVER_URL,
                {'app_id': self._app_id, 'game_id': self._game_id}
            )
        except api_open_live.TransportError:
            logger.error('room=%d _end_game() failed', self.room_id)
            return False
        except api_open_live.BusinessError as e:
            if e.code in (7000, 7003):
                # 项目已经关闭了也算成功
                return True
            logger.warning('room=%d _end_game() failed', self.room_id)
            return False
        return True

    async def _send_game_heartbeat(self):
        if self._game_id in (None, ''):
            logger.warning('game=%d _send_game_heartbeat() failed, game_id not found', self._game_id)
            return False

        # 保存一下，防止await之后game_id改变
        game_id = self._game_id
        try:
            await api_open_live.request_open_live_or_common_server(
                api_open_live.GAME_HEARTBEAT_OPEN_LIVE_URL,
                api_open_live.GAME_HEARTBEAT_COMMON_SERVER_URL,
                {'game_id': game_id}
            )
        except api_open_live.TransportError:
            logger.error('room=%d _send_game_heartbeat() failed', self.room_id)
            return False
        except api_open_live.BusinessError as e:
            logger.warning('room=%d _send_game_heartbeat() failed', self.room_id)
            if e.code == 7003 and self._game_id == game_id:
                # 项目异常关闭，可能是心跳超时，需要重新开启项目
                self._need_init_room = True
                if self._websocket is not None and not self._websocket.closed:
                    await self._websocket.close()
            return False
        return True


class ClientRoomManager:
    """管理到客户端的连接"""
    # 房间没有客户端后延迟多久删除房间，不立即删除防止短时间后重连
    DELAY_DEL_ROOM_TIMEOUT = 10

    def __init__(self):
        self._rooms: Dict[RoomKey, ClientRoom] = {}
        self._delay_del_timer_handles: Dict[RoomKey, asyncio.TimerHandle] = {}

    def shut_down(self):
        while len(self._rooms) != 0:
            room_key = next(iter(self._rooms))
            self.del_room(room_key)

        for timer_handle in self._delay_del_timer_handles.values():
            timer_handle.cancel()
        self._delay_del_timer_handles.clear()

    def add_client(self, room_key: RoomKey, client: 'api.chat.ChatHandler'):
        room = self._get_or_add_room(room_key)
        room.add_client(client)

        self._clear_delay_del_timer(room_key)

    def del_client(self, room_key: RoomKey, client: 'api.chat.ChatHandler'):
        room = self.get_room(room_key)
        if room is None:
            return

        room.del_client(client)

        if room.client_count == 0:
            self.delay_del_room(room_key, self.DELAY_DEL_ROOM_TIMEOUT)

    def get_room(self, room_key: RoomKey):
        return self._rooms.get(room_key, None)

    def _get_or_add_room(self, room_key: RoomKey):
        room = self._rooms.get(room_key, None)
        if room is None:
            logger.info('room=%s creating client room', room_key)
            self._rooms[room_key] = room = ClientRoom(room_key)
            logger.info('room=%s client room created, %d client rooms', room_key, len(self._rooms))

            _live_client_manager.add_live_client(room_key)
        return room

    def del_room(self, room_key: RoomKey):
        self._clear_delay_del_timer(room_key)

        room = self._rooms.pop(room_key, None)
        if room is None:
            return

        logger.info('room=%s removing client room', room_key)
        room.clear_clients()
        logger.info('room=%s client room removed, %d client rooms', room_key, len(self._rooms))

        _live_client_manager.del_live_client(room_key)

    def delay_del_room(self, room_key: RoomKey, timeout):
        self._clear_delay_del_timer(room_key)
        self._delay_del_timer_handles[room_key] = asyncio.get_running_loop().call_later(
            timeout, self._on_delay_del_room, room_key
        )

    def _clear_delay_del_timer(self, room_key: RoomKey):
        timer_handle = self._delay_del_timer_handles.pop(room_key, None)
        if timer_handle is not None:
            timer_handle.cancel()

    def _on_delay_del_room(self, room_key: RoomKey):
        self._delay_del_timer_handles.pop(room_key, None)
        self.del_room(room_key)


class ClientRoom:
    def __init__(self, room_key: RoomKey):
        self._room_key = room_key
        self._clients: List[api.chat.ChatHandler] = []
        self._auto_translate_count = 0

    @property
    def room_key(self) -> RoomKey:
        return self._room_key

    @property
    def client_count(self):
        return len(self._clients)

    @property
    def need_translate(self):
        return self._auto_translate_count > 0

    def add_client(self, client: 'api.chat.ChatHandler'):
        logger.info('room=%s addding client %s', self._room_key, client.request.remote_ip)

        self._clients.append(client)
        if client.auto_translate:
            self._auto_translate_count += 1

        logger.info('room=%s added client %s, %d clients', self._room_key, client.request.remote_ip,
                    self.client_count)

    def del_client(self, client: 'api.chat.ChatHandler'):
        client.close()
        try:
            self._clients.remove(client)
        except ValueError:
            return
        if client.auto_translate:
            self._auto_translate_count -= 1

        logger.info('room=%s removed client %s, %d clients', self._room_key, client.request.remote_ip,
                    self.client_count)

    def clear_clients(self):
        logger.info('room=%s clearing %d clients', self._room_key, self.client_count)

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
    def on_client_stopped(self, client: LiveClientType, exception: Optional[Exception]):
        _live_client_manager.del_live_client(client.room_key)

    def _on_danmaku(self, client: WebLiveClient, message: dm_web_models.DanmakuMessage):
        asyncio.create_task(self.__on_danmaku(client, message))

    async def __on_danmaku(self, client: WebLiveClient, message: dm_web_models.DanmakuMessage):
        avatar_url = message.face
        if avatar_url != '':
            services.avatar.update_avatar_cache_if_expired(message.uid, avatar_url)
        else:
            # 先异步调用再获取房间，因为返回时房间可能已经不存在了
            avatar_url = await services.avatar.get_avatar_url(message.uid)

        room = client_room_manager.get_room(client.room_key)
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

        need_translate = (
            content_type != api.chat.ContentType.EMOTICON and self._need_translate(message.msg, room, client)
        )
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
            await self._translate_and_response(message.msg, room.room_key, msg_id)

    def _on_gift(self, client: WebLiveClient, message: dm_web_models.GiftMessage):
        avatar_url = services.avatar.process_avatar_url(message.face)
        services.avatar.update_avatar_cache_if_expired(message.uid, avatar_url)

        # 丢人
        if message.coin_type != 'gold':
            return

        room = client_room_manager.get_room(client.room_key)
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

    def _on_buy_guard(self, client: WebLiveClient, message: dm_web_models.GuardBuyMessage):
        asyncio.create_task(self.__on_buy_guard(client, message))

    @staticmethod
    async def __on_buy_guard(client: WebLiveClient, message: dm_web_models.GuardBuyMessage):
        # 先异步调用再获取房间，因为返回时房间可能已经不存在了
        avatar_url = await services.avatar.get_avatar_url(message.uid)

        room = client_room_manager.get_room(client.room_key)
        if room is None:
            return

        room.send_cmd_data(api.chat.Command.ADD_MEMBER, {
            'id': uuid.uuid4().hex,
            'avatarUrl': avatar_url,
            'timestamp': message.start_time,
            'authorName': message.username,
            'privilegeType': message.guard_level
        })

    def _on_super_chat(self, client: WebLiveClient, message: dm_web_models.SuperChatMessage):
        avatar_url = services.avatar.process_avatar_url(message.face)
        services.avatar.update_avatar_cache_if_expired(message.uid, avatar_url)

        room = client_room_manager.get_room(client.room_key)
        if room is None:
            return

        need_translate = self._need_translate(message.message, room, client)
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
            asyncio.create_task(self._translate_and_response(
                message.message, room.room_key, msg_id, services.translate.Priority.HIGH
            ))

    def _on_super_chat_delete(self, client: WebLiveClient, message: dm_web_models.SuperChatDeleteMessage):
        room = client_room_manager.get_room(client.room_key)
        if room is None:
            return

        room.send_cmd_data(api.chat.Command.DEL_SUPER_CHAT, {
            'ids': list(map(str, message.ids))
        })

    @staticmethod
    def _need_translate(text, room: ClientRoom, client: LiveClientType):
        cfg = config.get_config()
        return (
            cfg.enable_translate
            and room.need_translate
            and (not cfg.allow_translate_rooms or client.room_id in cfg.allow_translate_rooms)
            and services.translate.need_translate(text)
        )

    @staticmethod
    async def _translate_and_response(text, room_key: RoomKey, msg_id, priority=services.translate.Priority.NORMAL):
        translation = await services.translate.translate(text, priority)
        if translation is None:
            return

        room = client_room_manager.get_room(room_key)
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

    #
    # 开放平台消息
    #

    def _on_open_live_danmaku(self, client: OpenLiveClient, message: dm_open_models.DanmakuMessage):
        avatar_url = message.uface
        services.avatar.update_avatar_cache_if_expired(message.uid, avatar_url)

        room = client_room_manager.get_room(client.room_key)
        if room is None:
            return

        if message.uid == client.room_owner_uid:
            author_type = 3  # 主播
        elif message.guard_level != 0:  # 1总督，2提督，3舰长
            author_type = 1  # 舰队
        else:
            author_type = 0

        if message.dm_type == 1:
            content_type = api.chat.ContentType.EMOTICON
            content_type_params = api.chat.make_emoticon_params(message.emoji_img_url)
        else:
            content_type = api.chat.ContentType.TEXT
            content_type_params = None

        need_translate = (
            content_type != api.chat.ContentType.EMOTICON and self._need_translate(message.msg, room, client)
        )
        if need_translate:
            translation = services.translate.get_translation_from_cache(message.msg)
            if translation is None:
                # 没有缓存，需要后面异步翻译后通知
                translation = ''
            else:
                need_translate = False
        else:
            translation = ''

        room.send_cmd_data(api.chat.Command.ADD_TEXT, api.chat.make_text_message_data(
            avatar_url=avatar_url,
            timestamp=message.timestamp,
            author_name=message.uname,
            author_type=author_type,
            content=message.msg,
            privilege_type=message.guard_level,
            medal_level=0 if not message.fans_medal_wearing_status else message.fans_medal_level,
            id_=message.msg_id,
            translation=translation,
            content_type=content_type,
            content_type_params=content_type_params,
        ))

        if need_translate:
            asyncio.create_task(self._translate_and_response(message.msg, room.room_key, message.msg_id))

    def _on_open_live_gift(self, client: OpenLiveClient, message: dm_open_models.GiftMessage):
        avatar_url = services.avatar.process_avatar_url(message.uface)
        services.avatar.update_avatar_cache_if_expired(message.uid, avatar_url)

        # 丢人
        if not message.paid:
            return

        room = client_room_manager.get_room(client.room_key)
        if room is None:
            return

        room.send_cmd_data(api.chat.Command.ADD_GIFT, {
            'id': message.msg_id,
            'avatarUrl': avatar_url,
            'timestamp': message.timestamp,
            'authorName': message.uname,
            'totalCoin': message.price,
            'giftName': message.gift_name,
            'num': message.gift_num
        })

    def _on_open_live_buy_guard(self, client: OpenLiveClient, message: dm_open_models.GuardBuyMessage):
        avatar_url = message.user_info.uface
        services.avatar.update_avatar_cache_if_expired(message.user_info.uid, avatar_url)

        room = client_room_manager.get_room(client.room_key)
        if room is None:
            return

        room.send_cmd_data(api.chat.Command.ADD_MEMBER, {
            'id': message.msg_id,
            'avatarUrl': avatar_url,
            'timestamp': message.timestamp,
            'authorName': message.user_info.uname,
            'privilegeType': message.guard_level
        })

    def _on_open_live_super_chat(self, client: OpenLiveClient, message: dm_open_models.SuperChatMessage):
        avatar_url = services.avatar.process_avatar_url(message.uface)
        services.avatar.update_avatar_cache_if_expired(message.uid, avatar_url)

        room = client_room_manager.get_room(client.room_key)
        if room is None:
            return

        need_translate = self._need_translate(message.message, room, client)
        if need_translate:
            translation = services.translate.get_translation_from_cache(message.message)
            if translation is None:
                # 没有缓存，需要后面异步翻译后通知
                translation = ''
            else:
                need_translate = False
        else:
            translation = ''

        msg_id = str(message.message_id)
        room.send_cmd_data(api.chat.Command.ADD_SUPER_CHAT, {
            'id': msg_id,
            'avatarUrl': avatar_url,
            'timestamp': message.start_time,
            'authorName': message.uname,
            'price': message.rmb,
            'content': message.message,
            'translation': translation
        })

        if need_translate:
            asyncio.create_task(self._translate_and_response(
                message.message, room.room_key, msg_id, services.translate.Priority.HIGH
            ))

    def _on_open_live_super_chat_delete(self, client: OpenLiveClient, message: dm_open_models.SuperChatDeleteMessage):
        room = client_room_manager.get_room(client.room_key)
        if room is None:
            return

        room.send_cmd_data(api.chat.Command.DEL_SUPER_CHAT, {
            'ids': list(map(str, message.message_ids))
        })
