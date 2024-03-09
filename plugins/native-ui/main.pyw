#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import logging.handlers
import os
import sys
from typing import *

import wxasync

import config
import designer.ui_base

logger = logging.getLogger('native-ui')

app: Optional[wxasync.WxAsyncApp] = None


async def main():
    try:
        await init()
        await run()
    finally:
        await shut_down()
    return 0


async def init():
    init_logging()

    global app
    app = wxasync.WxAsyncApp()

    # TODO 测试
    frame = designer.ui_base.RoomFrameBase(None)
    frame.chat_web_view.LoadURL('http://localhost:12450/room/test?minGiftPrice=0&showGiftName=true&relayMessagesByServer=true&lang=zh')
    frame.paid_web_view.LoadURL('http://localhost:12450/room/test?showDanmaku=false&showGiftName=true&relayMessagesByServer=true&lang=zh')
    frame.Show()

    app.SetTopWindow(frame)


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


async def run():
    logger.info('Running event loop')
    await app.MainLoop()
    logger.info('Start to shut down')


async def shut_down():
    pass


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
