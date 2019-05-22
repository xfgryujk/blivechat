# -*- coding: utf-8 -*-

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
    logging.basicConfig(
        format='{asctime} {levelname} [{name}]: {message}',
        datefmt='%Y-%m-%d %H:%M:%S',
        style='{',
        level=logging.INFO
    )

    app = tornado.web.Application([
        (r'/chat', chat.ChatHandler),
        (r'/((css|img|js)/.*)', tornado.web.StaticFileHandler, {'path': WEB_ROOT}),
        (r'/(favicon\.ico)', tornado.web.StaticFileHandler, {'path': WEB_ROOT}),
        (r'/.*', MainHandler, {'path': WEB_ROOT})
    ], websocket_ping_interval=30)
    app.listen(80, '127.0.0.1')
    logger.info('服务器启动：127.0.0.1:80')
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
