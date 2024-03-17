# -*- coding: utf-8 -*-
import __main__
import datetime
import logging
import os
import sys
from typing import *

import blcsdk
import blcsdk.models as sdk_models
import config

logger = logging.getLogger('msg-logging.' + __name__)

_msg_handler: Optional['MsgHandler'] = None
_id_room_dict: Dict[int, 'Room'] = {}


async def init():
    global _msg_handler
    _msg_handler = MsgHandler()
    blcsdk.set_msg_handler(_msg_handler)

    # 创建已有的房间。这一步失败了也没关系，只是有消息时才会创建文件
    try:
        blc_rooms = await blcsdk.get_rooms()
        for blc_room in blc_rooms:
            if blc_room.room_id is not None:
                _get_or_add_room(blc_room.room_id)
    except blcsdk.SdkError:
        pass


def shut_down():
    blcsdk.set_msg_handler(None)
    while len(_id_room_dict) != 0:
        room_id = next(iter(_id_room_dict))
        _del_room(room_id)


class MsgHandler(blcsdk.BaseHandler):
    def on_client_stopped(self, client: blcsdk.BlcPluginClient, exception: Optional[Exception]):
        logger.info('blivechat disconnected')
        __main__.start_shut_down()

    def _on_open_plugin_admin_ui(
        self, client: blcsdk.BlcPluginClient, message: sdk_models.OpenPluginAdminUiMsg, extra: sdk_models.ExtraData
    ):
        if sys.platform == 'win32':
            os.startfile(config.LOG_PATH)
        else:
            logger.info('Log path is "%s"', config.LOG_PATH)

    def _on_room_init(
        self, client: blcsdk.BlcPluginClient, message: sdk_models.RoomInitMsg, extra: sdk_models.ExtraData
    ):
        if extra.is_from_plugin:
            return
        if message.is_success:
            _get_or_add_room(extra.room_id)

    def _on_del_room(self, client: blcsdk.BlcPluginClient, message: sdk_models.DelRoomMsg, extra: sdk_models.ExtraData):
        if extra.is_from_plugin:
            return
        if extra.room_id is not None:
            _del_room(extra.room_id)

    def _on_add_text(self, client: blcsdk.BlcPluginClient, message: sdk_models.AddTextMsg, extra: sdk_models.ExtraData):
        if extra.is_from_plugin:
            return
        room = _get_or_add_room(extra.room_id)
        room.log(f'[dm] {message.author_name}：{message.content}')

    def _on_add_gift(self, client: blcsdk.BlcPluginClient, message: sdk_models.AddGiftMsg, extra: sdk_models.ExtraData):
        if extra.is_from_plugin:
            return
        room = _get_or_add_room(extra.room_id)
        if message.total_coin != 0:
            content = (
                f'[paid_gift] {message.author_name} 赠送了 {message.gift_name} x {message.num}，'
                f'总价 {message.total_coin / 1000:.1f} 元'
            )
        else:
            content = (
                f'[free_gift] {message.author_name} 赠送了 {message.gift_name} x {message.num}，'
                f'总价 {message.total_free_coin} 银瓜子'
            )
        room.log(content)

    def _on_add_member(
        self, client: blcsdk.BlcPluginClient, message: sdk_models.AddMemberMsg, extra: sdk_models.ExtraData
    ):
        if extra.is_from_plugin:
            return
        room = _get_or_add_room(extra.room_id)
        if message.privilege_type == sdk_models.GuardLevel.LV1:
            guard_name = '舰长'
        elif message.privilege_type == sdk_models.GuardLevel.LV2:
            guard_name = '提督'
        elif message.privilege_type == sdk_models.GuardLevel.LV3:
            guard_name = '总督'
        else:
            guard_name = '未知舰队等级'
        room.log(f'[guard] {message.author_name} 购买了 {message.num}{message.unit} {guard_name}，'
                 f'总价 {message.total_coin / 1000:.1f} 元')

    def _on_add_super_chat(
        self, client: blcsdk.BlcPluginClient, message: sdk_models.AddSuperChatMsg, extra: sdk_models.ExtraData
    ):
        if extra.is_from_plugin:
            return
        room = _get_or_add_room(extra.room_id)
        room.log(f'[superchat] {message.author_name} 发送了 {message.price} 元的醒目留言：{message.content}')


def _get_or_add_room(room_id):
    room = _id_room_dict.get(room_id, None)
    if room is None:
        if room_id is None:
            raise TypeError('room_id is None')
        room = _id_room_dict[room_id] = Room(room_id)
    return room


def _del_room(room_id):
    room = _id_room_dict.pop(room_id, None)
    if room is not None:
        room.close()


class Room:
    def __init__(self, room_id):
        cur_time = datetime.datetime.now()
        time_str = cur_time.strftime('%Y%m%d_%H%M%S')
        filename = f'room_{room_id}-{time_str}.txt'
        self._file = open(os.path.join(config.LOG_PATH, filename), 'a', encoding='utf-8-sig')

    def close(self):
        self._file.close()

    def log(self, content):
        cur_time = datetime.datetime.now()
        time_str = cur_time.strftime('%Y-%m-%d %H:%M:%S')
        text = f'{time_str} {content}\n'
        self._file.write(text)
        self._file.flush()
