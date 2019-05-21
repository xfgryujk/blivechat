# -*- coding: utf-8 -*-

import os

import tornado.ioloop
import tornado.web

WEB_ROOT = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')


# noinspection PyAbstractClass
class MainHandler(tornado.web.StaticFileHandler):
    """为了使用Vue Router的history模式，把所有请求转发到index.html"""
    async def get(self, *args, **kwargs):
        await super().get('index.html', *args, **kwargs)


def main():
    app = tornado.web.Application([
        (r'/((css|img|js)/.*)', tornado.web.StaticFileHandler, {'path': WEB_ROOT}),
        (r'/(favicon\.ico)', tornado.web.StaticFileHandler, {'path': WEB_ROOT}),
        (r'/.*', MainHandler, {'path': WEB_ROOT})
    ])
    app.listen(80, '127.0.0.1')
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
