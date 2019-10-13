# -*- coding: utf-8 -*-

import json

import tornado.web


# noinspection PyAbstractClass
class ApiHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        # 跨域测试用
        if not self.application.settings['debug']:
            return
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'OPTIONS, PUT, POST, GET, DELETE')
        if 'Access-Control-Request-Headers' in self.request.headers:
            self.set_header('Access-Control-Allow-Headers',
                            self.request.headers['Access-Control-Request-Headers'])

    def prepare(self):
        if self.request.headers.get('Content-Type', '').startswith('application/json'):
            try:
                self.json_args = json.loads(self.request.body)
            except json.JSONDecodeError:
                self.json_args = None
        else:
            self.json_args = None

    async def options(self, *_args, **_kwargs):
        # 跨域测试用
        self.set_status(204 if self.application.settings['debug'] else 405)
