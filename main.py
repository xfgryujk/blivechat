# -*- coding: utf-8 -*-

import argparse
import logging
import os
import webbrowser

import tornado.ioloop
import tornado.web

import api.chat
import api.main
import config
import models.avatar
import models.database
import update

logger = logging.getLogger(__name__)

WEB_ROOT = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')

routes = [
    (r'/chat', api.chat.ChatHandler),

    (r'/((css|fonts|img|js|static)/.*)', tornado.web.StaticFileHandler, {'path': WEB_ROOT}),
    (r'/(favicon\.ico)', tornado.web.StaticFileHandler, {'path': WEB_ROOT}),
    (r'/.*', api.main.MainHandler, {'path': WEB_ROOT})
]


def main():
    args = parse_args()

    init_logging(args.debug)
    config.init()
    models.database.init(args.debug)
    models.avatar.init()
    api.chat.init()
    update.check_update()

    run_server(args.host, args.port, args.debug)


def parse_args():
    parser = argparse.ArgumentParser(description='用于OBS的仿YouTube风格的bilibili直播聊天层')
    parser.add_argument('--host', help='服务器host，默认为127.0.0.1', default='127.0.0.1')
    parser.add_argument('--port', help='服务器端口，默认为12450', type=int, default=12450)
    parser.add_argument('--debug', help='调试模式', action='store_true')
    return parser.parse_args()


def init_logging(debug):
    logging.basicConfig(
        format='{asctime} {levelname} [{name}]: {message}',
        datefmt='%Y-%m-%d %H:%M:%S',
        style='{',
        level=logging.INFO if not debug else logging.DEBUG
    )


def run_server(host, port, debug):
    app = tornado.web.Application(
        routes,
        websocket_ping_interval=10,
        debug=debug,
        autoreload=False
    )
    try:
        app.listen(port, host)
    except OSError:
        logger.warning('Address is used %s:%d', host, port)
        return
    finally:
        url = 'http://localhost' if port == 80 else f'http://localhost:{port}'
        webbrowser.open(url)
    logger.info('Server started: %s:%d', host, port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
