# -*- coding: utf-8 -*-

import json
import os
from typing import Optional
from urllib.parse import urlencode

import pyperclip
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtGui import QIcon, QPixmap, QCloseEvent
from PyQt5.QtWidgets import QWidget, QDialog, QFileDialog, QInputDialog, QMessageBox, \
    QVBoxLayout, QListWidgetItem, QLabel

import config
from window import main
from window.desinger.ui_float_config import Ui_config_window

config_instance: Optional['FloatConfig'] = None


class FloatConfig(QDialog, Ui_config_window):
    def __init__(self):
        global config_instance
        QWidget.__init__(self)
        Ui_config_window.__init__(self)
        config_instance = self
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowIcon(QIcon(QPixmap(
            'frontend/dist/favicon.ico'
            if os.path.exists('frontend/dist/favicon.ico')
            else 'frontend/public/favicon.ico'
        )))
        self.setupUi(self)
        cfg = main.configs
        self.spin_box_room_id.valueChanged.connect(
            lambda t: self.update_url(cfg.update(roomId=self.spin_box_room_id.value()))
        )
        self.check_box_show_messages.clicked.connect(
            lambda: self.change_config('showDanmaku', self.check_box_show_messages.isChecked())
        )
        self.check_box_merge_similar_messages.clicked.connect(
            lambda: self.change_config('mergeSimilarDanmaku', self.check_box_merge_similar_messages.isChecked())
        )
        self.spin_box_max_number_of_messages.valueChanged.connect(
            lambda t: self.change_config('maxNumber', self.spin_box_max_number_of_messages.value())
        )
        self.check_box_show_shper_chats.clicked.connect(
            lambda: self.change_config('showGift', self.check_box_show_shper_chats.isChecked())
        )
        self.check_box_show_gift_name.clicked.connect(
            lambda: self.change_config('showGiftName', self.check_box_show_gift_name.isChecked())
        )
        self.check_box_merge_gifts.clicked.connect(
            lambda: self.change_config('mergeGift', self.check_box_merge_gifts.isChecked())
        )
        self.spin_box_min_price_of_super_chats_to_show.valueChanged.connect(
            lambda t: self.change_config('maxNumber', self.spin_box_min_price_of_super_chats_to_show.value())
        )
        self.check_box_block_system_messages.clicked.connect(
            lambda: self.change_config('blockGiftDanmaku', self.check_box_block_system_messages.isChecked())
        )
        self.check_box_block_informal_users.clicked.connect(
            lambda: self.change_config('blockNewbie', self.check_box_block_informal_users.isChecked())
        )
        self.check_box_block_unverified_users.clicked.connect(
            lambda: self.change_config('blockNotMobileVerified', self.check_box_block_unverified_users.isChecked())
        )
        self.horizontal_slider_block_user_level_lower_than.valueChanged.connect(
            lambda: self.change_config('blockLevel', self.horizontal_slider_block_user_level_lower_than.value())
        )
        self.horizontal_slider_block_user_level_lower_than.valueChanged.connect(
            self.spin_box_block_user_level_lower_than.setValue
        )
        self.spin_box_block_user_level_lower_than.valueChanged.connect(
            lambda: self.change_config('blockLevel', self.spin_box_block_user_level_lower_than.value())
        )
        self.spin_box_block_user_level_lower_than.valueChanged.connect(
            self.horizontal_slider_block_user_level_lower_than.setValue
        )
        self.horizontal_slider_block_medal_level_lower_than.valueChanged.connect(
            lambda: self.change_config('blockMedalLevel', self.horizontal_slider_block_medal_level_lower_than.value())
        )
        self.horizontal_slider_block_medal_level_lower_than.valueChanged.connect(
            self.spin_box_block_medal_level_lower_than.setValue
        )
        self.spin_box_block_medal_level_lower_than.valueChanged.connect(
            lambda: self.change_config('blockMedalLevel', self.spin_box_block_medal_level_lower_than.value())
        )
        self.spin_box_block_medal_level_lower_than.valueChanged.connect(
            self.horizontal_slider_block_medal_level_lower_than.setValue
        )
        self.text_edit_block_keywords.textChanged.connect(
            lambda: self.change_config('blockKeywords', self.text_edit_block_keywords.toPlainText())
        )
        self.text_edit_block_users.textChanged.connect(
            lambda: self.change_config('blockUsers', self.text_edit_block_users.toPlainText())
        )
        self.check_box_reply_message_by_server.clicked.connect(lambda: (
            self.change_config('relayMessagesByServer', self.check_box_reply_message_by_server.isChecked()),
            self.check_box_auto_translate_messages_to_japanese
                .setCheckable(self.check_box_reply_message_by_server.isChecked())
        ))
        self.check_box_reply_message_by_server.clicked.connect(
            lambda: self.change_config('autoTranslate', self.check_box_auto_translate_messages_to_japanese.isChecked())
        )
        self.radio_button_pronunciation_of_gift_username_none.clicked.connect(
            lambda: self.change_config('giftUsernamePronunciation', '')
        )
        self.radio_button_pronunciation_of_gift_username_pinyin.clicked.connect(
            lambda: self.change_config('giftUsernamePronunciation', 'pinyin')
        )
        self.radio_button_pronunciation_of_gift_username_kana.clicked.connect(
            lambda: self.change_config('giftUsernamePronunciation', 'kana')
        )
        self.push_button_copy_url.clicked.connect(lambda: pyperclip.copy(self.line_edit_room_url.text()))
        self.push_button_export_config.clicked.connect(self.export_config)
        self.push_button_import_config.clicked.connect(self.import_config)
        self.push_button_set_test_room.clicked.connect(lambda: self.update_url(cfg.update(roomId='test')))
        self.push_button_extra_css_add.clicked.connect(self.add_css)
        self.push_button_extra_css_add_url.clicked.connect(self.add_css_url)
        self.push_button_extra_css_remove.clicked.connect(self.remove_css)
        self.push_button_extra_css_edit.clicked.connect(self.edit_css)
        self.update_form()
        self.show()

    def closeEvent(self, e: QCloseEvent):
        super().closeEvent(e)
        main.save_config()

    def update_form(self):
        cfg = main.configs
        self.spin_box_room_id.setValue(int(cfg['roomId']) if 'test' != cfg['roomId'] else 0)
        self.check_box_show_messages.setChecked(cfg['roomConfig']['showDanmaku'])
        self.check_box_merge_similar_messages.setChecked(cfg['roomConfig']['mergeSimilarDanmaku'])
        self.spin_box_max_number_of_messages.setValue(cfg['roomConfig']['maxNumber'])
        self.check_box_show_shper_chats.setChecked(cfg['roomConfig']['showGift'])
        self.check_box_show_gift_name.setChecked(cfg['roomConfig']['showGiftName'])
        self.check_box_merge_gifts.setChecked(cfg['roomConfig']['mergeGift'])
        self.spin_box_min_price_of_super_chats_to_show.setValue(cfg['roomConfig']['maxNumber'])
        self.check_box_block_system_messages.setChecked(cfg['roomConfig']['blockGiftDanmaku'])
        self.check_box_block_informal_users.setChecked(cfg['roomConfig']['blockNewbie'])
        self.check_box_block_unverified_users.setChecked(cfg['roomConfig']['blockNotMobileVerified'])
        self.horizontal_slider_block_user_level_lower_than.setValue(cfg['roomConfig']['blockLevel'])
        self.spin_box_block_user_level_lower_than.setValue(cfg['roomConfig']['blockLevel'])
        self.horizontal_slider_block_medal_level_lower_than.setValue(cfg['roomConfig']['blockMedalLevel'])
        self.spin_box_block_medal_level_lower_than.setValue(cfg['roomConfig']['blockMedalLevel'])
        self.text_edit_block_keywords.setText(cfg['roomConfig']['blockKeywords'])
        self.text_edit_block_users.setText(cfg['roomConfig']['blockUsers'])
        self.check_box_reply_message_by_server.setChecked(cfg['roomConfig']['relayMessagesByServer'])
        self.check_box_auto_translate_messages_to_japanese.setChecked(cfg['roomConfig']['autoTranslate'])
        self.check_box_auto_translate_messages_to_japanese.setCheckable(cfg['roomConfig']['relayMessagesByServer'])
        {
            '': self.radio_button_pronunciation_of_gift_username_none,
            'pinyin': self.radio_button_pronunciation_of_gift_username_pinyin,
            'kana': self.radio_button_pronunciation_of_gift_username_kana
        }[cfg['roomConfig']['giftUsernamePronunciation']].setChecked(True)
        for url in main.configs['css']:
            self.add_list_widget_item(url)

    def change_config(self, key, value):
        main.configs['roomConfig'][key] = value
        self.update_url()

    def update_url(self, x=None):
        url = get_url()
        self.line_edit_room_url.setText(url)
        self.line_edit_room_url.home(True)
        main.room_url = url
        return x

    def export_config(self):
        path = QFileDialog.getSaveFileName(self, '保存配置文件', 'blivechat.json', 'JSON文件 (*.json)')[0]
        if '' != path:
            with open(path, 'w', encoding='UTF-8') as file:
                json.dump(main.configs['roomConfig'], file, ensure_ascii=False, indent=2)

    def import_config(self):
        path = QFileDialog.getOpenFileName(self, '打开配置文件', 'blivechat.json', 'JSON文件 (*.json)')[0]
        if '' != path:
            with open(path, 'r', encoding='UTF-8') as file:
                main.merge(main.configs['roomConfig'], json.load(file))
        self.update_form()
        self.update_url()

    def add_list_widget_item(self, url: QUrl):
        item = QListWidgetItem()
        item.setSizeHint(QSize(1, 50))
        self.list_widget_css_list.addItem(item)
        self.list_widget_css_list.setItemWidget(item, get_widget(url))

    def add_css(self):
        paths = QFileDialog.getOpenFileNames(self, '选择CSS', '', 'CSS文件 (*.css)')[0]
        for stylesheet in paths:
            for i in main.configs['css']:
                if i.isLocalFile() and os.path.samefile(i.toLocalFile(), stylesheet):
                    break
            else:
                url = QUrl.fromUserInput(os.path.normcase(stylesheet))
                self.add_list_widget_item(url)
                main.configs['css'].append(url)

    def add_css_url(self):
        path = QInputDialog.getText(self, '输入URL', '输入网络上CSS资源链接或本地文件的路径:')[0]
        if '' != path:
            for i in main.configs['css']:
                if (not i.isLocalFile()) and i.url() == path.lower():
                    break
            else:
                url = QUrl.fromUserInput(path.lower())
                self.add_list_widget_item(url)
                main.configs['css'].append(url)

    def remove_css(self):
        item = self.list_widget_css_list.currentItem()
        if item is not None and QMessageBox.Yes == QMessageBox.question(
                self, '删除？', '确定删除选中的样式表？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        ):
            row = self.list_widget_css_list.row(item)
            self.list_widget_css_list.takeItem(row)
            main.configs['css'].pop(row)

    def edit_css(self):
        item = self.list_widget_css_list.currentItem()
        row = self.list_widget_css_list.row(item)
        url_old = main.configs['css'][row]
        path = QInputDialog.getText(
            self, '修改URL', '输入网络上CSS资源链接或本地文件的路径:',
            text=url_old.toLocalFile() if url_old.isLocalFile() else url_old.url()
        )[0]
        if '' != path:
            url_new = QUrl.fromUserInput(path)
            main.configs['css'][row] = url_new
            self.list_widget_css_list.setItemWidget(item, get_widget(url_new))


def get_url():
    url = 'http://localhost%s/room/%s?%s' % (
        f':{main.args.port}' if main.args.port != 80 else '',
        main.configs['roomId'],
        urlencode(main.configs['roomConfig'])
    )
    loader_url = config.get_config().loader_url
    if '' != loader_url:
        url = f'{loader_url}?{urlencode({"url": url})}'
    return url


def get_widget(url: QUrl):
    widget = QWidget()
    vertical_layout = QVBoxLayout()
    label_name = QLabel()
    label_name.setText(url.fileName())
    vertical_layout.addWidget(label_name)
    label_path = QLabel()
    if url.isLocalFile():
        label_path.setText(url.toLocalFile().capitalize())
        label_path.setStyleSheet('font: 10px; font-weight: 600; color: gray;')
    else:
        label_path.setText(url.toDisplayString())
        label_path.setStyleSheet('font: 10px; font-weight: 600; color: darkblue;')
    vertical_layout.addWidget(label_path)
    widget.setLayout(vertical_layout)
    return widget
