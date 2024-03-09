#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import logging.handlers
import os
import signal
import sys
from typing import *

import wx
import wxasync

import blcsdk
import config
import listener

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
    init_signal_handlers()

    init_logging()

    await blcsdk.init()
    if not blcsdk.is_sdk_version_compatible():
        raise RuntimeError('SDK version is not compatible')

    init_ui()
    await listener.init()


def init_signal_handlers():
    signums = (signal.SIGINT, signal.SIGTERM)
    try:
        loop = asyncio.get_running_loop()
        for signum in signums:
            loop.add_signal_handler(signum, start_shut_down)
    except NotImplementedError:
        def signal_handler(*args):
            asyncio.get_running_loop().call_soon(start_shut_down, *args)

        # 不太安全，但Windows只能用这个
        for signum in signums:
            signal.signal(signum, signal_handler)


def start_shut_down(*_args):
    if app is not None:
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


def init_ui():
    global app
    app = wxasync.WxAsyncApp(clearSigInt=False)


async def run():
    logger.info('Running event loop')
    await app.MainLoop()
    logger.info('Start to shut down')


async def shut_down():
    listener.shut_down()
    await blcsdk.shut_down()


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
