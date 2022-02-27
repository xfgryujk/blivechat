# -*- coding: utf-8 -*-
import asyncio
import hashlib
import os

import tornado.web

import api.base
import config
import update


class MainHandler(tornado.web.StaticFileHandler):  # noqa
    """为了使用Vue Router的history模式，把不存在的文件请求转发到index.html"""
    async def get(self, path, include_body=True):
        try:
            await super().get(path, include_body)
        except tornado.web.HTTPError as e:
            if e.status_code != 404:
                raise
            # 不存在的文件请求转发到index.html，交给前端路由
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

        url = await asyncio.get_event_loop().run_in_executor(
            None, self._save_file, self.settings['WEB_ROOT'], file.body
        )
        self.write({
            'url': url
        })

    @staticmethod
    def _save_file(web_root, body):
        md5 = hashlib.md5(body).hexdigest()
        rel_path = os.path.join('upload', md5 + '.png')
        abs_path = os.path.join(web_root, rel_path)
        tmp_path = abs_path + '.tmp'
        with open(tmp_path, 'wb') as f:
            f.write(body)
        os.replace(tmp_path, abs_path)

        url = rel_path
        if os.path.sep != '/':
            url = url.replace(os.path.sep, '/')
        url = '/' + url
        return url
