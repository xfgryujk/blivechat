#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import concurrent.futures
import logging
import logging.handlers
import os
import signal
import threading
from typing import *

import pubsub.pub as pub
import wx

import blcsdk
import blcsdk.models as sdk_models
import config
import listener
import ui.room_config_dialog
import ui.room_frame
import ui.task_bar_icon

logger = logging.getLogger('native-ui')

app: Optional['App'] = None


def main():
    init_signal_handlers()

    init_logging()
    config.init()

    global app
    app = App()

    logger.info('Running event loop')
    app.MainLoop()


def init_signal_handlers():
    def signal_handler(*_args):
        wx.CallAfter(start_shut_down)

    for signum in (signal.SIGINT, signal.SIGTERM):
        signal.signal(signum, signal_handler)


def start_shut_down():
    if app is not None and app.IsMainLoopRunning():
        app.ExitMainLoop()
    else:
        wx.Exit()


def init_logging():
    filename = os.path.join(config.LOG_PATH, 'native-ui.log')
    stream_handler = logging.StreamHandler()
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename, encoding='utf-8', when='midnight', backupCount=7, delay=True
    )
    logging.basicConfig(
        format='{asctime} {levelname} [{name}]: {message}',
        style='{',
        level=logging.INFO,
        # level=logging.DEBUG,
        handlers=[stream_handler, file_handler],
    )


class App(wx.App):
    def __init__(self, *args, **kwargs):
        self._network_worker = NetworkWorker()

        self._dummy_timer: Optional[wx.Timer] = None
        self._task_bar_icon: Optional[ui.task_bar_icon.TaskBarIcon] = None

        self._key_room_frame_dict: Dict[sdk_models.RoomKey, ui.room_frame.RoomFrame] = {}
        self._room_config_dialog: Optional[ui.room_config_dialog.RoomConfigDialog] = None

        super().__init__(*args, clearSigInt=False, **kwargs)
        self.SetExitOnFrameDelete(False)

    def OnInit(self):
        # 这个定时器只是为了及时响应信号，因为只有处理UI事件时才会唤醒主线程
        self._dummy_timer = wx.Timer(self)
        self._dummy_timer.Start(1000)
        self.Bind(wx.EVT_TIMER, lambda _event: None, self._dummy_timer)

        self._task_bar_icon = ui.task_bar_icon.TaskBarIcon()

        pub.subscribe(self._on_add_room, 'add_room')
        pub.subscribe(self._on_del_room, 'del_room')
        pub.subscribe(self._on_room_frame_close, 'room_frame_close')
        pub.subscribe(self._on_add_room, 'open_room')
        pub.subscribe(self._on_open_room_config_dialog, 'open_room_config_dialog')

        self._network_worker.init()
        return True

    def OnExit(self):
        logger.info('Start to shut down')

        self._network_worker.start_shut_down()
        self._network_worker.join(10)

        return super().OnExit()

    def _on_add_room(self, room_key: sdk_models.RoomKey):
        if room_key in self._key_room_frame_dict:
            return

        room_frame = self._key_room_frame_dict[room_key] = ui.room_frame.RoomFrame(None, room_key)
        room_frame.Show()

    def _on_del_room(self, room_key: sdk_models.RoomKey):
        room_frame = self._key_room_frame_dict.pop(room_key, None)
        if room_frame is not None:
            room_frame.Close(True)

    def _on_room_frame_close(self, room_key: sdk_models.RoomKey):
        self._key_room_frame_dict.pop(room_key, None)

    def _on_open_room_config_dialog(self):
        if self._room_config_dialog is None or self._room_config_dialog.IsBeingDeleted():
            self._room_config_dialog = ui.room_config_dialog.RoomConfigDialog(None)
        self._room_config_dialog.Show()


class NetworkWorker:
    def __init__(self):
        self._worker_thread = threading.Thread(
            target=asyncio.run, args=(self._worker_thread_func(),), daemon=True
        )
        self._thread_init_future = concurrent.futures.Future()

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._shut_down_event: Optional[asyncio.Event] = None

    def init(self):
        self._worker_thread.start()
        self._thread_init_future.result(10)

    def start_shut_down(self):
        if self._shut_down_event is not None:
            self._loop.call_soon_threadsafe(self._shut_down_event.set)

    def join(self, timeout=None):
        self._worker_thread.join(timeout)
        return not self._worker_thread.is_alive()

    async def _worker_thread_func(self):
        self._loop = asyncio.get_running_loop()
        try:
            try:
                await self._init_in_worker_thread()
                self._thread_init_future.set_result(None)
            except BaseException as e:
                self._thread_init_future.set_exception(e)
                return

            await self._run()
        finally:
            await self._shut_down()

    async def _init_in_worker_thread(self):
        await blcsdk.init()
        if not blcsdk.is_sdk_version_compatible():
            raise RuntimeError('SDK version is not compatible')

        await listener.init()

        self._shut_down_event = asyncio.Event()

    async def _run(self):
        logger.info('Running network thread event loop')
        await self._shut_down_event.wait()
        logger.info('Network thread start to shut down')

    @staticmethod
    async def _shut_down():
        listener.shut_down()
        await blcsdk.shut_down()


if __name__ == '__main__':
    main()
