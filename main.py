#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import asyncio
import logging
import logging.handlers
import os
import signal
import sys
import webbrowser
from typing import *

import tornado.ioloop
import tornado.web

import api.chat
import api.main
import api.open_live
import api.plugin
import config
import models.database
import services.avatar
import services.chat
import services.open_live
import services.plugin
import services.translate
import update
import utils.request

logger = logging.getLogger(__name__)

ROUTES = [
    *api.main.ROUTES,
    *api.chat.ROUTES,
    *api.open_live.ROUTES,
    *api.plugin.ROUTES,
    *api.main.LAST_ROUTES,
]

server: Optional[tornado.httpserver.HTTPServer] = None

cmd_args = None
shut_down_event: Optional[asyncio.Event] = None


async def main():
    if not init():
        return 1
    try:
        await run()
    finally:
        await shut_down()
    return 0


def init():
    init_signal_handlers()

    global cmd_args
    cmd_args = parse_args()

    init_logging(cmd_args.debug)
    logger.info('App started, initializing')
    config.init(cmd_args)

    utils.request.init()
    models.database.init()

    services.avatar.init()
    services.translate.init()
    services.open_live.init()
    services.chat.init()

    init_server()
    if server is None:
        return False

    services.plugin.init()

    update.check_update()
    return True


def init_signal_handlers():
    global shut_down_event
    shut_down_event = asyncio.Event()

    is_win = sys.platform == 'win32'
    loop = asyncio.get_running_loop()
    if not is_win:
        def add_signal_handler(signum, callback):
            loop.add_signal_handler(signum, callback)
    else:
        def add_signal_handler(signum, callback):
            # 不太安全，但Windows只能用这个
            signal.signal(signum, lambda _signum, _frame: loop.call_soon(callback))

    shut_down_signums = (signal.SIGINT, signal.SIGTERM)
    if not is_win:
        reload_signum = signal.SIGHUP
    else:
        reload_signum = signal.SIGBREAK

    for shut_down_signum in shut_down_signums:
        add_signal_handler(shut_down_signum, on_shut_down_signal)
    add_signal_handler(reload_signum, on_reload_signal)


def on_shut_down_signal():
    shut_down_event.set()


def on_reload_signal():
    logger.info('Received reload signal')
    config.reload(cmd_args)


def parse_args():
    parser = argparse.ArgumentParser(description='用于OBS的仿YouTube风格的bilibili直播评论栏')
    parser.add_argument('--host', help='服务器host，默认和配置中的一样', default=None)
    parser.add_argument('--port', help='服务器端口，默认和配置中的一样', type=int, default=None)
    parser.add_argument('--debug', help='调试模式', action='store_true')
    return parser.parse_args()


def init_logging(debug):
    filename = os.path.join(config.BASE_PATH, 'log', 'blivechat.log')
    stream_handler = logging.StreamHandler()
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename, encoding='utf-8', when='midnight', backupCount=7, delay=True
    )
    logging.basicConfig(
        format='{asctime} {levelname} [{name}]: {message}',
        style='{',
        level=logging.INFO if not debug else logging.DEBUG,
        handlers=[stream_handler, file_handler]
    )

    # 屏蔽访问日志
    logging.getLogger('tornado.access').setLevel(logging.WARNING)


def init_server():
    cfg = config.get_config()
    app = tornado.web.Application(
        ROUTES,
        websocket_ping_interval=10,
        debug=cfg.debug,
        autoreload=False
    )
    try:
        global server
        server = app.listen(
            cfg.port,
            cfg.host,
            xheaders=cfg.tornado_xheaders,
            max_body_size=1024 * 1024,
            max_buffer_size=1024 * 1024
        )
    except OSError:
        logger.warning('Address is used %s:%d', cfg.host, cfg.port)
        return
    finally:
        if cfg.open_browser_at_startup:
            url = 'http://localhost/' if cfg.port == 80 else f'http://localhost:{cfg.port}/'
            webbrowser.open(url)
    logger.info('Server started: %s:%d', cfg.host, cfg.port)


async def run():
    logger.info('Running event loop')
    await shut_down_event.wait()
    logger.info('Received shutdown signal')


async def shut_down():
    services.plugin.shut_down()

    logger.info('Closing server')
    server.stop()
    await server.close_all_connections()

    logger.info('Closing websocket connections')
    await services.chat.shut_down()

    await utils.request.shut_down()

    logger.info('App shut down')


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
