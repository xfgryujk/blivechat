# -*- coding: utf-8 -*-
import __main__
import dataclasses
import datetime
import logging
from typing import *

import blcsdk
import blcsdk.models as sdk_models

logger = logging.getLogger('native-ui.' + __name__)

_msg_handler: Optional['MsgHandler'] = None
_key_room_dict: Dict[sdk_models.RoomKey, 'Room'] = {}


async def init():
    global _msg_handler
    _msg_handler = MsgHandler()
    blcsdk.set_msg_handler(_msg_handler)

    # 创建已有的房间。这一步失败了也没关系，只是有消息时才会创建房间
    try:
        blc_rooms = await blcsdk.get_rooms()
        for blc_room in blc_rooms:
            if blc_room.room_id is not None:
                _get_or_add_room(blc_room.room_key, blc_room.room_id)
    except blcsdk.SdkError:
        pass


def shut_down():
    blcsdk.set_msg_handler(None)


class MsgHandler(blcsdk.BaseHandler):
    def on_client_stopped(self, client: blcsdk.BlcPluginClient, exception: Optional[Exception]):
        logger.info('blivechat disconnected')
        __main__.start_shut_down()

    def _on_open_plugin_admin_ui(
        self, client: blcsdk.BlcPluginClient, message: sdk_models.OpenPluginAdminUiMsg, extra: sdk_models.ExtraData
    ):
        pass

    def _on_room_init(
        self, client: blcsdk.BlcPluginClient, message: sdk_models.RoomInitMsg, extra: sdk_models.ExtraData
    ):
        if extra.is_from_plugin:
            return
        if message.is_success:
            _get_or_add_room(extra.room_key, extra.room_id)

    def _on_del_room(self, client: blcsdk.BlcPluginClient, message: sdk_models.DelRoomMsg, extra: sdk_models.ExtraData):
        if extra.is_from_plugin:
            return
        if extra.room_id is not None:
            _del_room(extra.room_key)

    def _on_add_text(self, client: blcsdk.BlcPluginClient, message: sdk_models.AddTextMsg, extra: sdk_models.ExtraData):
        if extra.is_from_plugin:
            return
        room = _get_or_add_room(extra.room_key, extra.room_id)
        room.add_danmaku(message.uid)

    def _on_add_gift(self, client: blcsdk.BlcPluginClient, message: sdk_models.AddGiftMsg, extra: sdk_models.ExtraData):
        if extra.is_from_plugin:
            return
        room = _get_or_add_room(extra.room_key, extra.room_id)
        room.add_gift(GiftRecord(
            uid=str(message.uid),  # TODO SDK的uid改成Open ID
            author_name=message.author_name,
            gift_name=message.gift_name,
            num=message.num,
            price=message.total_coin / 1000,
        ))

    def _on_add_member(
        self, client: blcsdk.BlcPluginClient, message: sdk_models.AddMemberMsg, extra: sdk_models.ExtraData
    ):
        if extra.is_from_plugin:
            return
        room = _get_or_add_room(extra.room_key, extra.room_id)

        # 消息里没有价格，这里按最低算
        if message.privilege_type == sdk_models.GuardLevel.LV1:
            guard_name = '舰长'
            price = 138
        elif message.privilege_type == sdk_models.GuardLevel.LV2:
            guard_name = '提督'
            price = 1998
        elif message.privilege_type == sdk_models.GuardLevel.LV3:
            guard_name = '总督'
            price = 19998
        else:
            guard_name = '未知舰队等级'
            price = 0
        guard_name += f'（{message.unit}）'

        room.add_gift(GiftRecord(
            uid=str(message.uid),  # TODO SDK的uid改成Open ID
            author_name=message.author_name,
            gift_name=guard_name,
            num=message.num,
            price=price,
        ))

    def _on_add_super_chat(
        self, client: blcsdk.BlcPluginClient, message: sdk_models.AddSuperChatMsg, extra: sdk_models.ExtraData
    ):
        if extra.is_from_plugin:
            return
        room = _get_or_add_room(extra.room_key, extra.room_id)
        room.add_super_chat(SuperChatRecord(
            uid=str(message.uid),  # TODO SDK的uid改成Open ID
            author_name=message.author_name,
            price=message.price,
            content=message.content,
        ))


def get_room(room_key: sdk_models.RoomKey):
    return _key_room_dict.get(room_key, None)


def _get_or_add_room(room_key: sdk_models.RoomKey, room_id):
    room = _key_room_dict.get(room_key, None)
    if room is None:
        if room_id is None:
            raise TypeError('room_id is None')
        room = _key_room_dict[room_id] = Room(room_key, room_id)
        # TODO 打开房间窗口
    return room


def _del_room(room_key: sdk_models.RoomKey):
    _key_room_dict.pop(room_key, None)
    # TODO 关闭房间窗口


@dataclasses.dataclass
class SuperChatRecord:
    uid: str
    author_name: str
    price: float
    content: str
    time: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.now)


@dataclasses.dataclass
class GiftRecord:
    uid: str
    author_name: str
    gift_name: str
    num: int
    price: float
    time: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.now)


@dataclasses.dataclass
class PaidUserRecord:
    uid: str
    name: str
    price: float


class Room:
    def __init__(self, room_key: sdk_models.RoomKey, room_id: int):
        self._room_key = room_key
        self._room_id = room_id

        self._super_chats: List[SuperChatRecord] = []
        self._gifts: List[GiftRecord] = []
        self._uid_paid_user_dict: Dict[str, PaidUserRecord] = {}

        self._danmaku_num = 0
        self._interact_uids: Set[str] = set()
        self._total_paid_price = 0

    def add_danmaku(self, uid):
        self._danmaku_num += 1
        self._interact_uids.add(uid)

    def add_super_chat(self, super_chat: SuperChatRecord):
        self._super_chats.append(super_chat)
        self._add_user_paid_price(PaidUserRecord(
            uid=super_chat.uid,
            name=super_chat.author_name,
            price=super_chat.price,
        ))
        self._danmaku_num += 1
        self._interact_uids.add(super_chat.uid)
        self._total_paid_price += super_chat.price

    def add_gift(self, gift: GiftRecord):
        # 尝试合并
        is_merged = False
        min_time_to_merge = gift.time - datetime.timedelta(seconds=10)
        for old_gift in reversed(self._gifts):
            if old_gift.time < min_time_to_merge:
                break
            if old_gift.uid == gift.uid and old_gift.gift_name == gift.gift_name:
                old_gift.num += gift.num
                old_gift.price += gift.price
                is_merged = True
                break

        if not is_merged:
            self._gifts.append(gift)
        if gift.price > 0.:
            self._add_user_paid_price(PaidUserRecord(
                uid=gift.uid,
                name=gift.author_name,
                price=gift.price,
            ))
        self._interact_uids.add(gift.uid)
        self._total_paid_price += gift.price

    def _add_user_paid_price(self, paid_user: PaidUserRecord):
        old_paid_user = self._uid_paid_user_dict.get(paid_user.uid, None)
        if old_paid_user is None:
            old_paid_user = self._uid_paid_user_dict[paid_user.uid] = PaidUserRecord(
                uid=paid_user.uid,
                name=paid_user.name,
                price=0,
            )
        old_paid_user.price += paid_user.price
