# -*- coding: utf-8 -*-
import datetime
import logging
import urllib.parse
from typing import *

import pubsub.pub as pub
import wx
import xlsxwriter.exceptions

import blcsdk
import blcsdk.models as sdk_models
import config
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
        self.SetIcon(wx.Icon(config.BLC_ICON_PATH, wx.BITMAP_TYPE_ICO))

        self.super_chat_list.AppendColumn('时间', width=50)
        self.super_chat_list.AppendColumn('用户名', width=120)
        self.super_chat_list.AppendColumn('金额', width=50)
        self.super_chat_list.AppendColumn('内容', width=300)

        self.gift_list.AppendColumn('时间', width=50)
        self.gift_list.AppendColumn('用户名', width=120)
        self.gift_list.AppendColumn('礼物名', width=100)
        self.gift_list.AppendColumn('数量', width=50)
        self.gift_list.AppendColumn('总价', width=50)

        # item_data只能存int，这里做个映射
        self._uid_to_paid_user_item_data: Dict[str, int] = {}
        self._next_paid_user_item_data = 1
        self.paid_user_list.AppendColumn('用户名', width=120)
        self.paid_user_list.AppendColumn('总付费', width=60)

        self._apply_config(True)

        if room is not None:
            for index in range(len(room.super_chats)):
                self._on_super_chats_change(room, room.super_chats, index, True)
            for index in range(len(room.gifts)):
                self._on_gifts_change(room, room.gifts, index, True)
            for index in room.uid_paid_user_dict:
                self._on_uid_paid_user_dict_change(room, room.uid_paid_user_dict, index, True)
            self._on_simple_statistics_change(room)

        pub.subscribe(self._on_preview_room_opacity, 'preview_room_opacity')
        pub.subscribe(self._on_room_config_dialog_cancel, 'room_config_dialog_cancel')
        pub.subscribe(self._on_config_change, 'config_change')
        pub.subscribe(self._on_super_chats_change, 'room_data_change.super_chats')
        pub.subscribe(self._on_gifts_change, 'room_data_change.gifts')
        pub.subscribe(self._on_uid_paid_user_dict_change, 'room_data_change.uid_paid_user_dict')
        pub.subscribe(self._on_simple_statistics_change, 'room_data_change.danmaku_num')
        pub.subscribe(self._on_simple_statistics_change, 'room_data_change.interact_uids')
        pub.subscribe(self._on_simple_statistics_change, 'room_data_change.total_paid_price')

    #
    # 本窗口UI事件
    #

    def _on_close(self, event):
        pub.sendMessage('room_frame_close', room_key=self._room_key)
        super()._on_close(event)

    def _on_config_button_click(self, event):
        pub.sendMessage('open_room_config_dialog')

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

    def _on_export_excel_button_click(self, event):
        room = listener.get_room(self._room_key)
        room_str = str(room.room_id) if room is not None else str(self._room_key)
        cur_time = datetime.datetime.now()
        time_str = cur_time.strftime('%Y%m%d_%H%M%S')
        with wx.FileDialog(
            self,
            wildcard='Excel 文件 (*.xlsx)|*.xlsx',
            defaultFile=f'room_{room_str}-{time_str}.xlsx',
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
            name='导出Excel',
        ) as dialog:
            if dialog.ShowModal() != wx.ID_OK:
                return
            path = dialog.GetPath()

        try:
            with xlsxwriter.Workbook(path) as workbook:
                self._write_list_ctrl_to_workbook(self.super_chat_list, workbook, '醒目留言')
                self._write_list_ctrl_to_workbook(self.gift_list, workbook, '礼物&舰长')
                self._write_list_ctrl_to_workbook(self.paid_user_list, workbook, '付费用户')

                if room is not None:
                    sheet = workbook.add_worksheet('统计')
                    row_texts = ['总弹幕数', '互动用户数', '总付费']
                    sheet.write_column(0, 0, row_texts)
                    row_texts = [str(room.danmaku_num), str(len(room.interact_uids)), f'{room.total_paid_price:.1f}']
                    sheet.write_column(0, 1, row_texts)

                    sheet.set_column_pixels(0, 0, 120)

        except (OSError, xlsxwriter.exceptions.XlsxWriterException) as e:
            logger.exception('Failed to save excel file:')
            wx.MessageBox(str(e), '导出Excel失败', wx.OK | wx.ICON_ERROR | wx.CENTRE, self)

    def _write_list_ctrl_to_workbook(self, list_ctrl: wx.ListCtrl, workbook: xlsxwriter.Workbook, sheet_name):
        sheet = workbook.add_worksheet(sheet_name)
        for row, col_texts in enumerate(self._list_ctrl_to_col_texts(list_ctrl)):
            sheet.write_row(row, 0, col_texts)

        col_num = list_ctrl.GetColumnCount()
        for col in range(col_num):
            sheet.set_column_pixels(col, col, list_ctrl.GetColumnWidth(col))
        # sheet.autofit()

    @staticmethod
    def _list_ctrl_to_col_texts(list_ctrl: wx.ListCtrl):
        col_num = list_ctrl.GetColumnCount()
        row_num = list_ctrl.GetItemCount()
        yield [list_ctrl.GetColumn(col).GetText() for col in range(col_num)]
        for row in range(row_num):
            yield [list_ctrl.GetItemText(row, col) for col in range(col_num)]

    #
    # 配置事件
    #

    def _on_preview_room_opacity(self, room_opacity):
        self._set_opacity(room_opacity)

    def _set_opacity(self, opacity):
        opacity = min(max(opacity, 10), 100)
        alpha = round(opacity * wx.IMAGE_ALPHA_OPAQUE / 100)
        return self.SetTransparent(alpha)

    def _on_room_config_dialog_cancel(self):
        cfg = config.get_config()
        self._set_opacity(cfg.room_opacity)

    def _on_config_change(self, new_config: config.AppConfig, old_config: config.AppConfig):
        self._apply_config(new_config.is_url_params_changed(old_config))

    def _apply_config(self, reload_web_views):
        cfg = config.get_config()
        self._set_opacity(cfg.room_opacity)
        if reload_web_views:
            self.chat_web_view.LoadURL(self._get_room_url(cfg.chat_url_params))
            self.paid_web_view.LoadURL(self._get_room_url(cfg.paid_url_params, {'showDanmaku': 'false'}))

    def _get_room_url(self, params: dict, override_params: Optional[dict] = None):
        if override_params is None:
            override_params = {}
        params = {
            **params,
            'roomKeyType': self._room_key.type.value,
            'relayMessagesByServer': 'true',
            **override_params,
        }

        query = '&'.join(
            f'{urllib.parse.quote_plus(key)}={urllib.parse.quote_plus(str(value))}'
            for key, value in params.items()
        )
        blc_port = blcsdk.get_blc_port()
        encoded_room_key_value = urllib.parse.quote_plus(str(self._room_key.value))
        url = f'http://localhost:{blc_port}/room/{encoded_room_key_value}?{query}'
        return url

    #
    # 模型事件
    #

    def _on_super_chats_change(self, room: listener.Room, value: List[listener.SuperChatRecord], index, is_new):
        if room.room_key != self._room_key:
            return

        col_texts = self._super_chat_to_col_texts(value[index])
        self._update_list_ctrl(self.super_chat_list, index, is_new, col_texts)

    def _super_chat_to_col_texts(self, super_chat: listener.SuperChatRecord):
        return [
            self._format_time(super_chat.time),
            super_chat.author_name,
            f'{super_chat.price:.1f}',
            super_chat.content,
        ]

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

    def _on_gifts_change(self, room: listener.Room, value: List[listener.GiftRecord], index, is_new):
        if room.room_key != self._room_key:
            return

        col_texts = self._gift_to_col_texts(value[index])
        self._update_list_ctrl(self.gift_list, index, is_new, col_texts)

    def _gift_to_col_texts(self, gift: listener.GiftRecord):
        return [
            self._format_time(gift.time),
            gift.author_name,
            gift.gift_name,
            str(gift.num),
            f'{gift.price:.1f}',
        ]

    def _on_uid_paid_user_dict_change(
        self, room: listener.Room, value: Dict[str, listener.PaidUserRecord], index, is_new
    ):
        if room.room_key != self._room_key:
            return

        item_data = self._uid_to_paid_user_item_data.get(index, None)
        if item_data is None:
            item_data = self._uid_to_paid_user_item_data[index] = self._next_paid_user_item_data
            self._next_paid_user_item_data += 1

        col_texts = self._paid_user_to_col_texts(value[index])
        self._update_list_ctrl(self.paid_user_list, item_data, is_new, col_texts)

    @staticmethod
    def _paid_user_to_col_texts(paid_user: listener.PaidUserRecord):
        return [
            paid_user.name,
            f'{paid_user.price:.1f}',
        ]

    def _on_simple_statistics_change(self, room: listener.Room, value=None, index=None, is_new=None):  # noqa
        if room.room_key != self._room_key:
            return

        text = f'总弹幕数：{room.danmaku_num}  互动用户数：{len(room.interact_uids)}  总付费：{room.total_paid_price:.1f} 元'
        self.statistics_text.SetLabelText(text)
