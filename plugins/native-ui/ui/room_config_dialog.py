# -*- coding: utf-8 -*-
import copy
import logging
from typing import *

import pubsub.pub as pub
import wx

import config
import designer.ui_base

logger = logging.getLogger('native-ui.' + __name__)


class RoomConfigDialog(designer.ui_base.RoomConfigDialogBase):
    _GIFT_PRON_CHOICES = ('', 'pinyin', 'kana')

    def __init__(self, parent):
        super().__init__(parent)

        self._new_cfg_cache: Optional[config.AppConfig] = None

    def TransferDataToWindow(self):
        cfg = config.get_config()
        url_params: dict = cfg.chat_url_params

        self.opacity_slider.SetValue(cfg.room_opacity)
        self.auto_translate_check.SetValue(self._to_bool(url_params.get('autoTranslate', 'false')))
        try:
            gift_pron_index = self._GIFT_PRON_CHOICES.index(url_params.get('giftUsernamePronunciation', ''))
        except ValueError:
            gift_pron_index = 0
        self.gift_pron_choice.SetSelection(gift_pron_index)
        self.min_gift_price_edit.SetValue(url_params.get('minGiftPrice', '0'))
        self.block_gift_danmaku_check.SetValue(self._to_bool(url_params.get('blockGiftDanmaku', 'true')))

        return super().TransferDataToWindow()

    def _on_ok(self, event):
        try:
            self._new_cfg_cache = self._create_config_from_window()
        except Exception as e:
            logger.exception('_create_config_from_window failed:')
            wx.MessageBox(str(e), '应用设置失败', wx.OK | wx.ICON_ERROR | wx.CENTRE, self)
            return

        if (
            self._new_cfg_cache.is_url_params_changed(config.get_config())
            and wx.MessageBox(
                '修改部分设置需要刷新浏览器，是否继续？', '提示', wx.YES_NO | wx.CENTRE, self
            ) != wx.YES
        ):
            return
        super()._on_ok(event)

    def _create_config_from_window(self):
        cfg = copy.deepcopy(config.get_config())

        cfg.room_opacity = self.opacity_slider.GetValue()
        url_params = {
            'autoTranslate': self._bool_to_str(self.auto_translate_check.GetValue()),
            'giftUsernamePronunciation': self._GIFT_PRON_CHOICES[self.gift_pron_choice.GetSelection()],
            'minGiftPrice': self.min_gift_price_edit.GetValue(),
            'blockGiftDanmaku': self._bool_to_str(self.block_gift_danmaku_check.GetValue()),
        }
        cfg.chat_url_params.update(url_params)
        cfg.paid_url_params.update(url_params)

        return cfg

    def TransferDataFromWindow(self):
        if self._new_cfg_cache is None:
            logger.warning('_new_cfg_cache is None')
            return False

        config.set_config(self._new_cfg_cache)
        wx.CallAfter(self._new_cfg_cache.save, config.SAVE_CONFIG_PATH)

        return super().TransferDataFromWindow()

    def _on_cancel(self, event):
        pub.sendMessage('room_config_dialog_cancel')
        super()._on_cancel(event)

    @staticmethod
    def _to_bool(value):
        if isinstance(value, str):
            return value.lower() not in ('false', 'no', 'off', '0', '')
        return bool(value)

    @staticmethod
    def _bool_to_str(value):
        return 'true' if value else 'false'

    def _on_opacity_slider_change(self, event):
        pub.sendMessage('preview_room_opacity', room_opacity=self.opacity_slider.GetValue())
