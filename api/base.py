# -*- coding: utf-8 -*-
import json
from typing import *

import tornado.web

import config


class ApiHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_args: Optional[dict] = None

    def set_default_headers(self):
        self.set_header('Cache-Control', 'no-cache')

        self.add_header('Vary', 'Origin')
        origin = self.request.headers.get('Origin', None)
        if origin is None:
            return
        cfg = config.get_config()
        if not cfg.is_allowed_cors_origin(origin):
            return

        self.set_header('Access-Control-Allow-Origin', origin)
        self.set_header('Access-Control-Allow-Methods', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Max-Age', '3600')

    def prepare(self):
        if not self.request.headers.get('Content-Type', '').startswith('application/json'):
            return
        try:
            self.json_args = json.loads(self.request.body)
        except json.JSONDecodeError:
            pass

    async def options(self, *_args, **_kwargs):
        self.set_status(204)
