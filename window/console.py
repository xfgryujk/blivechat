# -*- coding: utf-8 -*-

import os
import re
import webbrowser
from typing import Optional

from PyQt5.QtGui import QPixmap, QIcon, QColor
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QAction, QMenu, QMessageBox

import window.main
from window.adjust import AdjustBox, TransformEdit
from window.browser import BrowserRoot
from window.desinger.ui_root import Ui_root
from window.setting import FloatConfig

MAX_COUNT_OF_MESSAGES = 1000
LEVEL_RE = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} (INFO|WARNING|ERROR|DEBUG|CRITICAL|NOTSET)')
STYLE = {
    'debug':    (QColor('#666666'), QColor('#ffffff')),
    'info':     (QColor('#1B1B1B'), QColor('#ffffff')),
    'warning':  (QColor('#5C3C00'), QColor('#FFFBE5')),
    'error':    (QColor('#E10000'), QColor('#FFF0F0')),
    'critical': (QColor('#792675'), QColor('#F8F0FF'))
}
window_frame_delta_width = 0
window_frame_delta_height = 0
browser_instance: Optional['BrowserRoot'] = None
adjust_box_instance: Optional['AdjustBox'] = None
transform_edit_instance: Optional['TransformEdit'] = None


class ConsoleWindow(QMainWindow, Ui_root):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_root.__init__(self)
        self.setupUi(self)
        icon = QIcon(QPixmap(
            'frontend/dist/favicon.ico' if os.path.exists(
                'frontend/dist/favicon.ico'
            ) else 'frontend/public/favicon.ico'
        ))
        self.setWindowIcon(icon)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(icon)
        self.tray_icon.activated[QSystemTrayIcon.ActivationReason].connect(self._tray_icon_click_handler)
        self.action_show_main_window = QAction('打开主界面', self)
        self.action_show_main_window.triggered.connect(self._tray_icon_click_handler)
        self.action_open_admin = QAction('在浏览器中打开管理页面', self)
        self.action_open_admin.setEnabled(False)
        self.action_open_admin.triggered.connect(lambda: None if webbrowser.open(window.main.config_url) else None)
        self.action_float_window = QAction('公屏聊天悬浮窗', self)
        self.action_float_window.setEnabled(False)
        self.action_float_window.setCheckable(True)
        self.action_float_window.setChecked(False)
        self.action_float_window.triggered.connect(self._float_window_handler)
        self.action_float_window_transform = QAction('位置和大小', self)
        self.action_float_window_transform.setCheckable(True)
        self.action_float_window_transform.setChecked(False)
        self.action_float_window_transform.triggered.connect(self._show_adjust_handler)
        self.action_float_window_transform_edit = QAction('缩放', self)
        self.action_float_window_transform_edit.setCheckable(True)
        self.action_float_window_transform_edit.setChecked(False)
        self.action_float_window_transform_edit.triggered.connect(self._show_scale_edit)
        self.menu_float_window_adjust = QMenu('悬浮窗调整', self)
        self.menu_float_window_adjust.addAction(self.action_float_window_transform)
        self.menu_float_window_adjust.addAction(self.action_float_window_transform_edit)
        self.action_float_window_config = QAction('悬浮窗设置', self)
        self.action_float_window_config.triggered.connect(self._float_window_config_handler)
        self.action_stop = QAction('关闭服务', self)
        self.action_stop.triggered.connect(self._stop_handler)
        self.menu_tray_icon = QMenu(self)
        self.menu_tray_icon.addAction(self.action_show_main_window)
        self.menu_tray_icon.addSeparator()
        self.menu_tray_icon.addAction(self.action_open_admin)
        self.menu_tray_icon.addSeparator()
        self.menu_tray_icon.addAction(self.action_float_window)
        self.menu_tray_icon.addMenu(self.menu_float_window_adjust)
        self.menu_tray_icon.addAction(self.action_float_window_config)
        self.menu_tray_icon.addSeparator()
        self.menu_tray_icon.addAction(self.action_stop)
        self.tray_icon.setContextMenu(self.menu_tray_icon)
        self.tray_icon.show()
        self.button_open_admin.clicked.connect(lambda: webbrowser.open(window.main.config_url))
        self.button_float_window.clicked.connect(self._float_window_handler)
        self.button_float_window_config.clicked.connect(self._float_window_config_handler)
        self.button_stop.clicked.connect(self._stop_handler)
        self.show()
        # 窗体宽高与客户区宽高的差（边框的宽高），用以修正 AdjustBox.resize()。
        global window_frame_delta_width, window_frame_delta_height
        window_frame_delta_width = self.frameGeometry().width() - self.width()
        window_frame_delta_height = self.frameGeometry().height() - self.height()

    def _show_scale_edit(self):
        global transform_edit_instance
        if transform_edit_instance is not None:
            transform_edit_instance.close()
        else:
            transform_edit_instance = TransformEdit()
            self.action_float_window_transform_edit.setChecked(True)

    def _show_adjust_handler(self):
        global adjust_box_instance
        if adjust_box_instance is not None:
            adjust_box_instance.close()
        else:
            adjust_box_instance = AdjustBox()
            self.action_float_window_transform.setChecked(True)

    def _float_window_handler(self):
        global browser_instance
        if browser_instance is not None:
            browser_instance.close()
        else:
            browser_instance = BrowserRoot()
            self.button_float_window.setText('关闭浮窗')
            self.action_float_window.setChecked(True)

    @staticmethod
    def _float_window_config_handler():
        FloatConfig()

    def _stop_handler(self):
        if QMessageBox.Yes == QMessageBox.question(
                self, '关闭？', '要关闭服务器并退出吗？这会使已经打开的直播评论栏无法正常更新！',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        ):
            window.main.app.quit()

    def _tray_icon_click_handler(self, reason):
        if QSystemTrayIcon.DoubleClick == reason:
            self.showNormal()
            self.activateWindow()


class ConsoleHandler(object):
    @staticmethod
    def write(message):
        if '\n' != message:
            lev = ConsoleHandler.get_lev(message)
            q_list_widget_item = QListWidgetItem(message, window.main.console.list_widget_console)
            q_list_widget_item.setForeground(STYLE[lev][0])
            q_list_widget_item.setBackground(STYLE[lev][1])
            if window.main.console.list_widget_console.count() > MAX_COUNT_OF_MESSAGES:
                window.main.console.list_widget_console.takeItem(0)

    @staticmethod
    def get_lev(msg):
        lev = LEVEL_RE.findall(msg)
        if len(lev) > 0:
            return lev[0].lower()
