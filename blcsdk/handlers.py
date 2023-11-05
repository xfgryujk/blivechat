# -*- coding: utf-8 -*-
from typing import *

from . import client as cli
from . import models

__all__ = (
    'HandlerInterface',
    'BaseHandler',
)


class HandlerInterface:
    """blivechat插件消息处理器接口"""

    def handle(self, client: cli.BlcPluginClient, command: dict):
        raise NotImplementedError

    def on_client_stopped(self, client: cli.BlcPluginClient, exception: Optional[Exception]):
        """
        当客户端停止时调用

        这种情况说明blivechat已经退出了，或者插件被禁用了，因此重连基本会失败。这里唯一建议的操作是退出当前程序
        """


def _make_msg_callback(method_name, message_cls):
    def callback(self: 'BaseHandler', client: cli.BlcPluginClient, command: dict):
        method = getattr(self, method_name)
        msg = message_cls.from_command(command['data'])
        extra = models.ExtraData.from_dict(command.get('extra', {}))
        return method(client, msg, extra)
    return callback


class BaseHandler(HandlerInterface):
    """一个简单的消息处理器实现，带消息分发和消息类型转换。继承并重写_on_xxx方法即可实现自己的处理器"""

    _CMD_CALLBACK_DICT: Dict[
        int,
        Optional[Callable[
            ['BaseHandler', cli.BlcPluginClient, dict],
            Any
        ]]
    ] = {
        models.Command.ADD_ROOM: _make_msg_callback('_on_add_room', models.AddRoomMsg),
        models.Command.ROOM_INIT: _make_msg_callback('_on_room_init', models.RoomInitMsg),
        models.Command.DEL_ROOM: _make_msg_callback('_on_del_room', models.DelRoomMsg),
        models.Command.ADD_TEXT: _make_msg_callback('_on_add_text', models.AddTextMsg),
        models.Command.ADD_GIFT: _make_msg_callback('_on_add_gift', models.AddGiftMsg),
        models.Command.ADD_MEMBER: _make_msg_callback('_on_add_member', models.AddMemberMsg),
        models.Command.ADD_SUPER_CHAT: _make_msg_callback('_on_add_super_chat', models.AddSuperChatMsg),
        models.Command.DEL_SUPER_CHAT: _make_msg_callback('_on_del_super_chat', models.DelSuperChatMsg),
        models.Command.UPDATE_TRANSLATION: _make_msg_callback('_on_update_translation', models.UpdateTranslationMsg),
    }
    """cmd -> 处理回调"""

    def handle(self, client: cli.BlcPluginClient, command: dict):
        cmd = command['cmd']
        callback = self._CMD_CALLBACK_DICT.get(cmd, None)
        if callback is not None:
            callback(self, client, command)

    def _on_add_room(self, client: cli.BlcPluginClient, message: models.AddRoomMsg, extra: models.ExtraData):
        """添加房间"""

    def _on_room_init(self, client: cli.BlcPluginClient, message: models.RoomInitMsg, extra: models.ExtraData):
        """房间初始化"""

    def _on_del_room(self, client: cli.BlcPluginClient, message: models.DelRoomMsg, extra: models.ExtraData):
        """删除房间"""

    def _on_add_text(self, client: cli.BlcPluginClient, message: models.AddTextMsg, extra: models.ExtraData):
        """收到弹幕"""

    def _on_add_gift(self, client: cli.BlcPluginClient, message: models.AddGiftMsg, extra: models.ExtraData):
        """有人送礼"""

    def _on_add_member(self, client: cli.BlcPluginClient, message: models.AddMemberMsg, extra: models.ExtraData):
        """有人上舰"""

    def _on_add_super_chat(self, client: cli.BlcPluginClient, message: models.AddSuperChatMsg, extra: models.ExtraData):
        """醒目留言"""

    def _on_del_super_chat(self, client: cli.BlcPluginClient, message: models.DelSuperChatMsg, extra: models.ExtraData):
        """删除醒目留言"""

    def _on_update_translation(
        self, client: cli.BlcPluginClient, message: models.UpdateTranslationMsg, extra: models.ExtraData
    ):
        """更新翻译"""
