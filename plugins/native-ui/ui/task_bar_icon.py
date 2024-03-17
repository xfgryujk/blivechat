# -*- coding: utf-8 -*-
import logging
import sys
import webbrowser

import pubsub.pub as pub
import wx.adv

import blcsdk
import config
import listener

if sys.platform == 'win32':
    IS_WIN = True
    # 懒得引入pywin32了
    import ctypes
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32
else:
    IS_WIN = False


logger = logging.getLogger('native-ui.' + __name__)


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self):
        super().__init__()

        self.SetIcon(wx.Icon(config.BLC_ICON_PATH, wx.BITMAP_TYPE_ICO), 'blivechat')

        self._menu = wx.Menu()
        self._menu.Append(1, '打开所有房间窗口')
        self._menu.Append(2, '打开主页')
        if IS_WIN:
            self._menu.Append(3, '隐藏/显示控制台')
            self._menu.Append(wx.ID_SEPARATOR)
            self._menu.Append(wx.ID_EXIT, '退出')

        self.Bind(wx.adv.EVT_TASKBAR_LEFT_UP, self._on_open_all_rooms_click)
        self.Bind(wx.EVT_MENU, self._on_open_all_rooms_click, id=1)
        self.Bind(wx.EVT_MENU, self._on_open_browser_click, id=2)
        self.Bind(wx.EVT_MENU, self._on_hide_console_click, id=3)
        self.Bind(wx.EVT_MENU, self._on_exit_click, id=wx.ID_EXIT)

        pub.subscribe(self._on_open_admin_ui, 'open_admin_ui')

    def _on_open_admin_ui(self):
        self.PopupMenu(self.GetPopupMenu())

    def GetPopupMenu(self):
        return self._menu

    @staticmethod
    def _on_open_browser_click(_event):
        blc_port = blcsdk.get_blc_port()
        url = 'http://localhost/' if blc_port == 80 else f'http://localhost:{blc_port}/'
        webbrowser.open(url)

    @staticmethod
    def _on_open_all_rooms_click(_event):
        room_keys = [room.room_key for room in listener.iter_rooms()]
        if not room_keys:
            wx.MessageBox('没有任何已连接的房间', '提示')
            return

        for room_key in room_keys:
            pub.sendMessage('open_room', room_key=room_key)

    def _on_hide_console_click(self, _event):
        assert IS_WIN
        console_window_handle = self._find_console_window()
        if console_window_handle == 0:
            logger.warning('Console window not found')
            wx.MessageBox('找不到控制台窗口', '提示')
            return

        is_visible = user32.IsWindowVisible(console_window_handle)
        show_param = 0 if is_visible else 5  # SW_HIDE SW_SHOW
        user32.ShowWindowAsync(console_window_handle, show_param)

    @staticmethod
    def _find_console_window():
        assert IS_WIN
        console_window_handle: int = kernel32.GetConsoleWindow()
        if console_window_handle == 0:
            return 0
        # 兼容Windows Terminal，https://github.com/microsoft/terminal/issues/12464
        while True:
            parent_window_handle: int = user32.GetParent(console_window_handle)
            if parent_window_handle == 0:
                break
            console_window_handle = parent_window_handle
        return console_window_handle

    def _on_exit_click(self, _event):
        assert IS_WIN
        # 先恢复控制台显示，防止退出后无法恢复
        console_window_handle = self._find_console_window()
        if console_window_handle != 0 and not user32.IsWindowVisible(console_window_handle):
            user32.ShowWindowAsync(console_window_handle, 5)  # SW_SHOW

        kernel32.GenerateConsoleCtrlEvent(0, 0)  # CTRL_C_EVENT
