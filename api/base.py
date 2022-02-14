# -*- coding: utf-8 -*-
import json

import tornado.web


class ApiHandler(tornado.web.RequestHandler):  # noqa
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_args = None

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
        if not self.request.headers.get('Content-Type', '').startswith('application/json'):
            return
        try:
            self.json_args = json.loads(self.request.body)
        except json.JSONDecodeError:
            pass

    async def options(self, *_args, **_kwargs):
        # 跨域测试用
        self.set_status(204 if self.application.settings['debug'] else 405)
