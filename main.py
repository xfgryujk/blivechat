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
import config
import models.database
import services.avatar
import services.chat
import services.translate
import update
import utils.request

logger = logging.getLogger(__name__)

ROUTES = [
    *api.main.ROUTES,
    *api.chat.ROUTES,
    *api.open_live.ROUTES,
    *api.main.LAST_ROUTES,
]

server: Optional[tornado.httpserver.HTTPServer] = None

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

    args = parse_args()

    init_logging(args.debug)
    logger.info('App started, initializing')
    config.init()

    utils.request.init()
    models.database.init(args.debug)

    services.avatar.init()
    services.translate.init()
    services.chat.init()

    update.check_update()

    init_server(args.host, args.port, args.debug)
    return server is not None


def init_signal_handlers():
    global shut_down_event
    shut_down_event = asyncio.Event()

    signums = (signal.SIGINT, signal.SIGTERM)
    try:
        loop = asyncio.get_running_loop()
        for signum in signums:
            loop.add_signal_handler(signum, on_shut_down_signal)
    except NotImplementedError:
        # 不太安全，但Windows只能用这个
        for signum in signums:
            signal.signal(signum, on_shut_down_signal)


def on_shut_down_signal(*_args):
    shut_down_event.set()


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


def init_server(host, port, debug):
    cfg = config.get_config()
    if host is None:
        host = cfg.host
    if port is None:
        port = cfg.port

    app = tornado.web.Application(
        ROUTES,
        websocket_ping_interval=10,
        debug=debug,
        autoreload=False
    )
    try:
        global server
        server = app.listen(
            port,
            host,
            xheaders=cfg.tornado_xheaders,
            max_body_size=1024 * 1024,
            max_buffer_size=1024 * 1024
        )
    except OSError:
        logger.warning('Address is used %s:%d', host, port)
        return
    finally:
        if cfg.open_browser_at_startup:
            url = 'http://localhost/' if port == 80 else f'http://localhost:{port}/'
            webbrowser.open(url)
    logger.info('Server started: %s:%d', host, port)


async def run():
    logger.info('Running event loop')
    await shut_down_event.wait()
    logger.info('Received shutdown signal')


async def shut_down():
    logger.info('Closing server')
    server.stop()
    await server.close_all_connections()

    logger.info('Closing websocket connections')
    await services.chat.shut_down()

    await utils.request.shut_down()

    logger.info('App shut down')


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
