# -*- coding: utf-8 -*-

import tornado.web

import api.base
import config
import update


class MainHandler(tornado.web.StaticFileHandler):
    """为了使用Vue Router的history模式，把所有请求转发到index.html"""
    async def get(self, *args, **kwargs):
        await super().get('index.html', *args, **kwargs)


# noinspection PyAbstractClass
class ServerInfoHandler(api.base.ApiHandler):
    async def get(self):
        cfg = config.get_config()
        self.write({
            'version': update.VERSION,
            'config': {
                'enableTranslate': cfg.enable_translate
            }
        })
