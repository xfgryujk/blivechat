# -*- coding: utf-8 -*-
import asyncio
import hashlib
import logging
import os

import tornado.web

import api.base
import config
import update

logger = logging.getLogger(__name__)

EMOTICON_UPLOAD_PATH = os.path.join(config.DATA_PATH, 'emoticons')
EMOTICON_BASE_URL = '/emoticons'


class MainHandler(tornado.web.StaticFileHandler):  # noqa
    """为了使用Vue Router的history模式，把不存在的文件请求转发到index.html"""
    async def get(self, path, include_body=True):
        if path == '':
            await self._get_index(include_body)
            return

        try:
            await super().get(path, include_body)
        except tornado.web.HTTPError as e:
            if e.status_code != 404:
                raise
            # 不存在的文件请求转发到index.html，交给前端路由
            await self._get_index(include_body)

    async def _get_index(self, include_body=True):
        # index.html不缓存，防止更新后前端还是旧版
        self.set_header('Cache-Control', 'no-cache')
        await super().get('index.html', include_body)


class ServerInfoHandler(api.base.ApiHandler):  # noqa
    async def get(self):
        cfg = config.get_config()
        self.write({
            'version': update.VERSION,
            'config': {
                'enableTranslate': cfg.enable_translate,
                'enableUploadFile': cfg.enable_upload_file,
                'loaderUrl': cfg.loader_url
            }
        })


class UploadEmoticonHandler(api.base.ApiHandler):  # noqa
    async def post(self):
        cfg = config.get_config()
        if not cfg.enable_upload_file:
            raise tornado.web.HTTPError(403)

        try:
            file = self.request.files['file'][0]
        except LookupError:
            raise tornado.web.MissingArgumentError('file')
        if len(file.body) > 1024 * 1024:
            raise tornado.web.HTTPError(413, 'file is too large, size=%d', len(file.body))
        if not file.content_type.lower().startswith('image/'):
            raise tornado.web.HTTPError(415)

        url = await asyncio.get_running_loop().run_in_executor(
            None, self._save_file, file.body, self.request.remote_ip
        )
        self.write({
            'url': url
        })

    @staticmethod
    def _save_file(body, client):
        md5 = hashlib.md5(body).hexdigest()
        filename = md5 + '.png'
        path = os.path.join(EMOTICON_UPLOAD_PATH, filename)
        logger.info('client=%s uploaded file, path=%s, size=%d', client, path, len(body))

        tmp_path = path + '.tmp'
        with open(tmp_path, 'wb') as f:
            f.write(body)
        os.replace(tmp_path, path)

        return f'{EMOTICON_BASE_URL}/{filename}'
