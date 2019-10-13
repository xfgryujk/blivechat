# -*- coding: utf-8 -*-

import json
import uuid

import views.base
from typing import *

MAX_CONFIG_SIZE = 100 * 1024

configs: Dict[str, dict] = {}


# noinspection PyAbstractClass
class ConfigsHandler(views.base.ApiHandler):
    async def post(self):
        if not isinstance(self.json_args, dict):
            self.set_status(400)
            return

        config = self.json_args
        config_id = str(uuid.uuid4())
        config['id'] = config_id
        config_str = json.dumps(config)
        if len(config_str) > MAX_CONFIG_SIZE:
            self.set_status(413)
            return

        configs[config_id] = config
        self.write(config_str)
        self.set_status(201)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

        if len(configs) > 10000:
            for _, key in zip(range(100), configs):
                del configs[key]


# noinspection PyAbstractClass
class ConfigHandler(views.base.ApiHandler):
    async def put(self, config_id):
        if config_id not in configs:
            self.set_status(404)
            return
        if not isinstance(self.json_args, dict):
            self.set_status(400)
            return

        config = self.json_args
        config['id'] = config_id
        config_str = json.dumps(config)
        if len(config_str) > MAX_CONFIG_SIZE:
            self.set_status(413)
            return

        configs[config_id] = config
        self.write(config_str)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

    async def get(self, config_id):
        config = configs.get(config_id, None)
        if config is None:
            self.set_status(404)
            return
        self.write(config)
