# -*- coding: utf-8 -*-

import uuid

import views.base
from typing import *

configs: Dict[str, dict] = {}

ALLOWED_FIELDS = (
    'minGiftPrice', 'mergeSimilarDanmaku', 'blockGiftDanmaku', 'blockLevel',
    'blockNewbie', 'blockNotMobileVerified', 'blockKeywords', 'blockUsers',
    'css'
)


# noinspection PyAbstractClass
class ConfigsHandler(views.base.ApiHandler):
    async def post(self):
        config_id = str(uuid.uuid4())
        config = {
            name: self.json_args[name] for name in ALLOWED_FIELDS
        }
        config['id'] = config_id
        configs[config_id] = config
        self.set_status(201)
        self.write(config)

        if len(configs) > 10000:
            for _, key in zip(range(100), configs):
                del configs[key]


# noinspection PyAbstractClass
class ConfigHandler(views.base.ApiHandler):
    async def put(self, config_id):
        config = configs.get(config_id, None)
        if config is None:
            self.set_status(404)
            return
        for name in ALLOWED_FIELDS:
            config[name] = self.json_args[name]
        self.write(config)

    async def get(self, config_id):
        config = configs.get(config_id, None)
        if config is None:
            self.set_status(404)
            return
        self.write(config)
