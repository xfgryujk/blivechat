#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import logging.handlers
import os
import signal
import sys
from typing import *

import blcsdk
import config
import listener

logger = logging.getLogger('msg-logging')

shut_down_event: Optional[asyncio.Event] = None


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

    await listener.init()


def init_signal_handlers():
    global shut_down_event
    shut_down_event = asyncio.Event()

    signums = (signal.SIGINT, signal.SIGTERM)
    try:
        loop = asyncio.get_running_loop()
        for signum in signums:
            loop.add_signal_handler(signum, start_shut_down)
    except NotImplementedError:
        # 不太安全，但Windows只能用这个
        for signum in signums:
            signal.signal(signum, start_shut_down)


def start_shut_down(*_args):
    shut_down_event.set()


def init_logging():
    filename = os.path.join(config.LOG_PATH, 'msg-logging.log')
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
    await shut_down_event.wait()
    logger.info('Start to shut down')


async def shut_down():
    await blcsdk.shut_down()


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
