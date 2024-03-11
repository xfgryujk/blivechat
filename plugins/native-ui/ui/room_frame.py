# -*- coding: utf-8 -*-
import datetime
import logging
import urllib.parse
from typing import *

import pubsub.pub as pub
import wx

import blcsdk
import blcsdk.models as sdk_models
import designer.ui_base
import listener

logger = logging.getLogger('native-ui.' + __name__)


class RoomFrame(designer.ui_base.RoomFrameBase):
    def __init__(self, parent, room_key: sdk_models.RoomKey):
        super().__init__(parent)
        self._room_key = room_key

        room = listener.get_room(self._room_key)
        room_str = str(room.room_id) if room is not None else str(self._room_key)
        self.SetTitle(f'blivechat - 房间 {room_str}')

        room_params = {'minGiftPrice': 0, 'showGiftName': 'true'}
        self.chat_web_view.LoadURL(self._get_room_url(room_params))
        room_params['showDanmaku'] = 'false'
        self.paid_web_view.LoadURL(self._get_room_url(room_params))

        self.super_chat_list.AppendColumn('时间', width=50)
        self.super_chat_list.AppendColumn('用户名', width=120)
        self.super_chat_list.AppendColumn('金额', width=50)
        self.super_chat_list.AppendColumn('内容', width=300)
        for index in range(len(room.super_chats)):
            self._on_super_chats_change(room, room.super_chats, index, True)

        self.gift_list.AppendColumn('时间', width=50)
        self.gift_list.AppendColumn('用户名', width=120)
        self.gift_list.AppendColumn('礼物名', width=100)
        self.gift_list.AppendColumn('数量', width=50)
        self.gift_list.AppendColumn('总价', width=50)
        for index in range(len(room.gifts)):
            self._on_gifts_change(room, room.gifts, index, True)

        # item_data只能存int，这里做个映射
        self._uid_to_paid_user_item_data: Dict[str, int] = {}
        self._next_paid_user_item_data = 1
        self.paid_user_list.AppendColumn('用户名', width=120)
        self.paid_user_list.AppendColumn('总付费', width=60)
        for index in room.uid_paid_user_dict:
            self._on_uid_paid_user_dict_change(room, room.uid_paid_user_dict, index, True)

        pub.subscribe(self._on_super_chats_change, 'room_data_change.super_chats')
        pub.subscribe(self._on_gifts_change, 'room_data_change.gifts')
        pub.subscribe(self._on_uid_paid_user_dict_change, 'room_data_change.uid_paid_user_dict')
        pub.subscribe(self._on_simple_statistics_change, 'room_data_change.danmaku_num')
        pub.subscribe(self._on_simple_statistics_change, 'room_data_change.interact_uids')
        pub.subscribe(self._on_simple_statistics_change, 'room_data_change.total_paid_price')

    def _get_room_url(self, params: dict):
        params = params.copy()
        params['roomKeyType'] = self._room_key.type.value
        params['relayMessagesByServer'] = 'true'

        query = '&'.join(
            f'{urllib.parse.quote_plus(key)}={urllib.parse.quote_plus(str(value))}'
            for key, value in params.items()
        )
        blc_port = blcsdk.get_blc_port()
        encoded_room_key_value = urllib.parse.quote_plus(str(self._room_key.value))
        url = f'http://localhost:{blc_port}/room/{encoded_room_key_value}?{query}'
        return url

    #
    # UI事件
    #

    def _on_close(self, event):
        pub.sendMessage('room_frame_close', room_key=self._room_key)
        super()._on_close(event)

    def _on_config_button_click(self, event):
        # TODO WIP
        dialog = designer.ui_base.RoomConfigDialogBase(self)
        dialog.Show()

    def _on_stay_on_top_button_toggle(self, event: wx.CommandEvent):
        style = self.GetWindowStyle()
        if event.IsChecked():
            style |= wx.STAY_ON_TOP
        else:
            style &= ~wx.STAY_ON_TOP
        self.SetWindowStyle(style)

    def _on_collapse_console_button_click(self, event):
        window_size = self.GetSize()
        if self.console_notebook.IsShown():
            window_size.Scale(0.5, 1)
            self.console_notebook.Hide()
            self.collapse_console_button.SetLabelText('<<')
        else:
            window_size.Scale(2, 1)
            self.console_notebook.Show()
            self.collapse_console_button.SetLabelText('>>')
        self.SetSize(window_size)
        self.Layout()

    #
    # 模型事件
    #

    def _on_super_chats_change(self, room: listener.Room, value: List[listener.SuperChatRecord], index, is_new):  # noqa
        if room.room_key != self._room_key:
            return

        super_chat = value[index]
        col_texts = [
            self._format_time(super_chat.time),
            super_chat.author_name,
            f'{super_chat.price:.1f}',
            super_chat.content,
        ]
        self._update_list_ctrl(self.super_chat_list, index, is_new, col_texts)

    @staticmethod
    def _format_time(time: datetime.datetime):
        return time.strftime('%H:%M')

    def _update_list_ctrl(self, list_ctrl: wx.ListCtrl, item_data: int, is_new, col_texts: List[str]):
        if is_new:
            row_index = list_ctrl.Append(col_texts)
            list_ctrl.SetItemData(row_index, item_data)

            self._maybe_scroll_list_ctrl_to_bottom(list_ctrl)
            return

        for row_index in range(list_ctrl.GetItemCount() - 1, -1, -1):
            if list_ctrl.GetItemData(row_index) != item_data:
                continue
            for col_index, text in enumerate(col_texts):
                list_ctrl.SetItem(row_index, col_index, text)
            break

    @staticmethod
    def _maybe_scroll_list_ctrl_to_bottom(list_ctrl: wx.ListCtrl):
        """如果原来就在底端则滚动到底端"""
        last_row_index = list_ctrl.GetItemCount() - 1
        if last_row_index < 0:
            return

        # 没有找到更简单的方法
        list_height = list_ctrl.GetClientSize().GetHeight() * list_ctrl.GetContentScaleFactor()
        last_row_rect = list_ctrl.GetItemRect(max(last_row_index, 0))
        height_to_bottom = last_row_rect.GetBottom() - list_height
        if height_to_bottom < last_row_rect.GetHeight() * 3:
            list_ctrl.Focus(last_row_index)

    def _on_gifts_change(self, room: listener.Room, value: List[listener.GiftRecord], index, is_new):  # noqa
        if room.room_key != self._room_key:
            return

        gift = value[index]
        col_texts = [
            self._format_time(gift.time),
            gift.author_name,
            gift.gift_name,
            str(gift.num),
            f'{gift.price:.1f}',
        ]
        self._update_list_ctrl(self.gift_list, index, is_new, col_texts)

    def _on_uid_paid_user_dict_change(
        self, room: listener.Room, value: Dict[str, listener.PaidUserRecord], index, is_new  # noqa
    ):
        if room.room_key != self._room_key:
            return

        item_data = self._uid_to_paid_user_item_data.get(index, None)
        if item_data is None:
            item_data = self._uid_to_paid_user_item_data[index] = self._next_paid_user_item_data
            self._next_paid_user_item_data += 1

        paid_user = value[index]
        col_texts = [
            paid_user.name,
            f'{paid_user.price:.1f}',
        ]
        self._update_list_ctrl(self.paid_user_list, item_data, is_new, col_texts)

    def _on_simple_statistics_change(self, room: listener.Room, value=None, index=None, is_new=None):  # noqa
        if room.room_key != self._room_key:
            return

        text = f'总弹幕数：{room.danmaku_num}  互动用户数：{len(room.interact_uids)}  总付费：{room.total_paid_price:.1f} 元'
        self.statistics_text.SetLabelText(text)
