# -*- coding: utf-8 -*-

import tornado.web


# noinspection PyAbstractClass
class MainHandler(tornado.web.StaticFileHandler):
    """为了使用Vue Router的history模式，把所有请求转发到index.html"""
    async def get(self, *args, **kwargs):
        await super().get('index.html', *args, **kwargs)
