# -*- coding: utf-8 -*-
import json
from typing import *

import tornado.web


class ApiHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_args: Optional[dict] = None

    def prepare(self):
        self.set_header('Cache-Control', 'no-cache')

        if not self.request.headers.get('Content-Type', '').startswith('application/json'):
            return
        try:
            self.json_args = json.loads(self.request.body)
        except json.JSONDecodeError:
            pass
