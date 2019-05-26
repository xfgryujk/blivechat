# -*- coding: utf-8 -*-

import argparse
import logging
import os

import tornado.ioloop
import tornado.web

import chat

logger = logging.getLogger(__name__)

WEB_ROOT = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')


# noinspection PyAbstractClass
class MainHandler(tornado.web.StaticFileHandler):
    """为了使用Vue Router的history模式，把所有请求转发到index.html"""
    async def get(self, *args, **kwargs):
        await super().get('index.html', *args, **kwargs)


def main():
    parser = argparse.ArgumentParser(description='用于OBS的仿YouTube风格的bilibili直播聊天层')
    parser.add_argument('--host', help='服务器host，默认为127.0.0.1', default='127.0.0.1')
    parser.add_argument('--port', help='服务器端口，默认为80', type=int, default=80)
    parser.add_argument('--debug', help='调试模式', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(
        format='{asctime} {levelname} [{name}]: {message}',
        datefmt='%Y-%m-%d %H:%M:%S',
        style='{',
        level=logging.INFO if not args.debug else logging.DEBUG
    )

    app = tornado.web.Application(
        [
            (r'/chat', chat.ChatHandler),
            (r'/((css|img|js)/.*)', tornado.web.StaticFileHandler, {'path': WEB_ROOT}),
            (r'/(favicon\.ico)', tornado.web.StaticFileHandler, {'path': WEB_ROOT}),
            (r'/.*', MainHandler, {'path': WEB_ROOT})
        ],
        websocket_ping_interval=30,
        debug=args.debug,
        autoreload=False
    )
    app.listen(args.port, args.host)
    logger.info('服务器启动：%s:%d', args.host, args.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
