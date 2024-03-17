# -*- coding: utf-8 -*-
import logging
from typing import *

import pubsub.pub as pub
import wxasync

import blcsdk.models as sdk_models
import ui.room_config_dialog
import ui.room_frame
import ui.task_bar_icon

logger = logging.getLogger('native-ui.' + __name__)

_app: Optional['App'] = None


def init():
    global _app
    _app = App()


class App(wxasync.WxAsyncApp):
    def __init__(self, *args, **kwargs):
        self._task_bar_icon: Optional[ui.task_bar_icon.TaskBarIcon] = None

        super().__init__(*args, clearSigInt=False, **kwargs)
        self.SetExitOnFrameDelete(False)

        self._key_room_frame_dict: Dict[sdk_models.RoomKey, ui.room_frame.RoomFrame] = {}
        self._room_config_dialog: Optional[ui.room_config_dialog.RoomConfigDialog] = None

    def OnInit(self):
        self._task_bar_icon = ui.task_bar_icon.TaskBarIcon()

        pub.subscribe(self._on_add_room, 'add_room')
        pub.subscribe(self._on_del_room, 'del_room')
        pub.subscribe(self._on_room_frame_close, 'room_frame_close')
        pub.subscribe(self._on_add_room, 'open_room')
        pub.subscribe(self._on_open_room_config_dialog, 'open_room_config_dialog')
        return True

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
