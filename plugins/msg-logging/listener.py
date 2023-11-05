# -*- coding: utf-8 -*-
import __main__
import datetime
import logging
import os
from typing import *

import blcsdk
import blcsdk.models as sdk_models
import config
from blcsdk import client as cli

logger = logging.getLogger(__name__)

_msg_handler: Optional['MsgHandler'] = None
_id_room_dict: Dict[int, 'Room'] = {}


async def init():
    global _msg_handler
    _msg_handler = MsgHandler()
    blcsdk.set_msg_handler(_msg_handler)

    # TODO 创建已有的房间


def shut_down():
    blcsdk.set_msg_handler(None)
    while _id_room_dict:
        room_id = next(iter(_id_room_dict))
        _del_room(room_id)


class MsgHandler(blcsdk.BaseHandler):
    def on_client_stopped(self, client: cli.BlcPluginClient, exception: Optional[Exception]):
        logger.info('blivechat disconnected')
        __main__.start_shut_down()

    def _on_room_init(self, client: cli.BlcPluginClient, message: sdk_models.RoomInitMsg, extra: sdk_models.ExtraData):
        if message.is_success:
            _get_or_add_room(extra.room_id)

    def _on_del_room(self, client: cli.BlcPluginClient, message: sdk_models.DelRoomMsg, extra: sdk_models.ExtraData):
        if extra.room_id is not None:
            _del_room(extra.room_id)

    def _on_add_text(self, client: cli.BlcPluginClient, message: sdk_models.AddTextMsg, extra: sdk_models.ExtraData):
        room = _get_or_add_room(extra.room_id)
        room.log(f'[dm] {message.author_name}：{message.content}')

    def _on_add_gift(self, client: cli.BlcPluginClient, message: sdk_models.AddGiftMsg, extra: sdk_models.ExtraData):
        room = _get_or_add_room(extra.room_id)
        room.log(
            f'[gift] {message.author_name} 赠送了 {message.gift_name} x {message.num}，'
            f'总价 {message.total_coin / 1000} 元'
        )

    def _on_add_member(
        self, client: cli.BlcPluginClient, message: sdk_models.AddMemberMsg, extra: sdk_models.ExtraData
    ):
        room = _get_or_add_room(extra.room_id)
        if message.privilege_type == sdk_models.GuardLevel.LV1:
            guard_name = '舰长'
        elif message.privilege_type == sdk_models.GuardLevel.LV2:
            guard_name = '提督'
        elif message.privilege_type == sdk_models.GuardLevel.LV3:
            guard_name = '总督'
        else:
            guard_name = '未知舰队等级'
        # TODO 可以加上时长
        room.log(f'[guard] {message.author_name} 购买了 {guard_name}')

    def _on_add_super_chat(
        self, client: cli.BlcPluginClient, message: sdk_models.AddSuperChatMsg, extra: sdk_models.ExtraData
    ):
        room = _get_or_add_room(extra.room_id)
        room.log(f'[superchat] {message.author_name} 发送了 {message.price} 元的醒目留言：{message.content}')


def _get_or_add_room(room_id):
    ctx = _id_room_dict.get(room_id, None)
    if ctx is None:
        ctx = _id_room_dict[room_id] = Room(room_id)
    return ctx


def _del_room(room_id):
    ctx = _id_room_dict.pop(room_id, None)
    if ctx is not None:
        ctx.close()


class Room:
    def __init__(self, room_id):
        self.room_id = room_id

        cur_time = datetime.datetime.now()
        time_str = cur_time.strftime('%Y%m%d_%H%M%S')
        filename = f'room_{room_id}-{time_str}.log'
        self.file = open(os.path.join(config.LOG_PATH, filename), 'a', encoding='utf-8-sig')

    def close(self):
        self.file.close()

    def log(self, content):
        cur_time = datetime.datetime.now()
        time_str = cur_time.strftime('%Y-%m-%d %H:%M:%S')
        text = f'{time_str} {content}\n'
        self.file.write(text)
        self.file.flush()
