# -*- coding: utf-8 -*-
import designer.ui_base


class RoomFrame(designer.ui_base.RoomFrameBase):
    def __init__(self, parent):
        super().__init__(parent)

        self.chat_web_view.LoadURL('http://localhost:12450/room/test?minGiftPrice=0&showGiftName=true&relayMessagesByServer=true&lang=zh')
        self.paid_web_view.LoadURL('http://localhost:12450/room/test?showDanmaku=false&showGiftName=true&relayMessagesByServer=true&lang=zh')
