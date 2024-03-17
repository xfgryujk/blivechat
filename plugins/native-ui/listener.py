# -*- coding: utf-8 -*-
import __main__
import dataclasses
import datetime
import logging
from typing import *

import pubsub.pub as pub
import wx

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
                wx.CallAfter(_get_or_add_room, blc_room.room_key, blc_room.room_id)
    except blcsdk.SdkError:
        pass


def shut_down():
    blcsdk.set_msg_handler(None)


class MsgHandler(blcsdk.BaseHandler):
    def on_client_stopped(self, client: blcsdk.BlcPluginClient, exception: Optional[Exception]):
        logger.info('blivechat disconnected')
        wx.CallAfter(__main__.start_shut_down)

    def handle(self, client: blcsdk.BlcPluginClient, command: dict):
        wx.CallAfter(super().handle, client, command)

    def _on_open_plugin_admin_ui(
        self, client: blcsdk.BlcPluginClient, message: sdk_models.OpenPluginAdminUiMsg, extra: sdk_models.ExtraData
    ):
        pub.sendMessage('open_admin_ui')

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
            uid=message.uid,
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

        if message.privilege_type == sdk_models.GuardLevel.LV1:
            guard_name = '舰长'
        elif message.privilege_type == sdk_models.GuardLevel.LV2:
            guard_name = '提督'
        elif message.privilege_type == sdk_models.GuardLevel.LV3:
            guard_name = '总督'
        else:
            guard_name = '未知舰队等级'
        guard_name += f'（{message.unit}）'

        room.add_gift(GiftRecord(
            uid=message.uid,
            author_name=message.author_name,
            gift_name=guard_name,
            num=message.num,
            price=message.total_coin / 1000,
        ))

    def _on_add_super_chat(
        self, client: blcsdk.BlcPluginClient, message: sdk_models.AddSuperChatMsg, extra: sdk_models.ExtraData
    ):
        if extra.is_from_plugin:
            return
        room = _get_or_add_room(extra.room_key, extra.room_id)
        room.add_super_chat(SuperChatRecord(
            uid=message.uid,
            author_name=message.author_name,
            price=message.price,
            content=message.content,
        ))


def iter_rooms() -> Iterable['Room']:
    return _key_room_dict.values()


def get_room(room_key: sdk_models.RoomKey):
    return _key_room_dict.get(room_key, None)


def _get_or_add_room(room_key: sdk_models.RoomKey, room_id):
    room = _key_room_dict.get(room_key, None)
    if room is None:
        if room_id is None:
            raise TypeError('room_id is None')
        room = _key_room_dict[room_key] = Room(room_key, room_id)
        pub.sendMessage('add_room', room_key=room_key)
    return room


def _del_room(room_key: sdk_models.RoomKey):
    room = _key_room_dict.pop(room_key, None)
    if room is not None:
        pub.sendMessage('del_room', room_key=room_key)


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

    @property
    def room_key(self):
        return self._room_key

    @property
    def room_id(self):
        return self._room_id

    @property
    def super_chats(self):
        return self._super_chats

    @property
    def gifts(self):
        return self._gifts

    @property
    def uid_paid_user_dict(self):
        return self._uid_paid_user_dict

    @property
    def danmaku_num(self):
        return self._danmaku_num

    @property
    def interact_uids(self):
        return self._interact_uids

    @property
    def total_paid_price(self):
        return self._total_paid_price

    def add_danmaku(self, uid):
        self._danmaku_num += 1
        pub.sendMessage('room_data_change.danmaku_num', room=self, value=self._danmaku_num)

        self._add_interact_uid(uid)

    def _add_interact_uid(self, uid):
        if uid in self._interact_uids:
            return

        self._interact_uids.add(uid)
        pub.sendMessage(
            'room_data_change.interact_uids',
            room=self,
            value=self._interact_uids,
            index=uid,
            is_new=True,
        )

    def add_super_chat(self, super_chat: SuperChatRecord):
        self._super_chats.append(super_chat)
        pub.sendMessage(
            'room_data_change.super_chats',
            room=self,
            value=self._super_chats,
            index=len(self._super_chats) - 1,
            is_new=True,
        )

        self._add_user_paid_price(PaidUserRecord(
            uid=super_chat.uid,
            name=super_chat.author_name,
            price=super_chat.price,
        ))

        self._total_paid_price += super_chat.price
        pub.sendMessage('room_data_change.total_paid_price', room=self, value=self._total_paid_price)

        self.add_danmaku(super_chat.uid)

    def _add_user_paid_price(self, paid_user: PaidUserRecord):
        old_paid_user = self._uid_paid_user_dict.get(paid_user.uid, None)
        if old_paid_user is None:
            old_paid_user = self._uid_paid_user_dict[paid_user.uid] = PaidUserRecord(
                uid=paid_user.uid,
                name=paid_user.name,
                price=0,
            )
            is_new = True
        else:
            is_new = False
        old_paid_user.price += paid_user.price

        pub.sendMessage(
            'room_data_change.uid_paid_user_dict',
            room=self,
            value=self._uid_paid_user_dict,
            index=paid_user.uid,
            is_new=is_new,
        )

    def add_gift(self, gift: GiftRecord):
        # 尝试合并
        is_merged = False
        min_time_to_merge = gift.time - datetime.timedelta(seconds=10)
        index = len(self._gifts)
        for index in range(len(self._gifts) - 1, -1, -1):
            old_gift = self._gifts[index]

            if old_gift.time < min_time_to_merge:
                break
            if old_gift.uid == gift.uid and old_gift.gift_name == gift.gift_name:
                old_gift.num += gift.num
                old_gift.price += gift.price
                is_merged = True
                break
        if not is_merged:
            index = len(self._gifts)
            self._gifts.append(gift)
        pub.sendMessage(
            'room_data_change.gifts',
            room=self,
            value=self._gifts,
            index=index,
            is_new=not is_merged,
        )

        if gift.price > 0.:
            self._add_user_paid_price(PaidUserRecord(
                uid=gift.uid,
                name=gift.author_name,
                price=gift.price,
            ))

        self._add_interact_uid(gift.uid)

        self._total_paid_price += gift.price
        pub.sendMessage('room_data_change.total_paid_price', room=self, value=self._total_paid_price)
