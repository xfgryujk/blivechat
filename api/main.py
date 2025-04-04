# -*- coding: utf-8 -*-
import asyncio
import hashlib
import json
import logging
import os

import cachetools
import tornado.web
import yarl

import api.base
import config
import update

logger = logging.getLogger(__name__)

EMOTICON_UPLOAD_PATH = os.path.join(config.DATA_PATH, 'emoticons')
EMOTICON_BASE_URL = '/emoticons'
CUSTOM_PUBLIC_PATH = os.path.join(config.DATA_PATH, 'custom_public')
TEMPLATE_PATH = os.path.join(CUSTOM_PUBLIC_PATH, 'templates')
TEMPLATE_BASE_URL = '/custom_public/templates'

_templates_cache = cachetools.TTLCache(1, 10)


class StaticHandler(tornado.web.StaticFileHandler):
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


class ServerInfoHandler(api.base.ApiHandler):
    async def get(self):
        cfg = config.get_config()
        self.write({
            'version': update.VERSION,
            'config': {
                'enableTranslate': cfg.enable_translate,
                'enableUploadFile': cfg.enable_upload_file,
                'loaderUrl': cfg.loader_url,
                'enableAdminPlugins': cfg.enable_admin_plugins,
            }
        })


class ServiceDiscoveryHandler(api.base.ApiHandler):
    async def get(self):
        cfg = config.get_config()
        self.write({
            'endpoints': cfg.registered_endpoints,
        })


class PingHandler(api.base.ApiHandler):
    async def get(self):
        self.set_status(204)


class UploadEmoticonHandler(api.base.ApiHandler):
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
        self.write({'url': url})

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


class TemplatesHandler(api.base.ApiHandler):
    async def get(self):
        templates = _templates_cache.get('templates', None)
        if templates is None:
            templates = await asyncio.get_running_loop().run_in_executor(None, self._get_templates)
            _templates_cache['templates'] = templates

        self.set_header('Cache-Control', 'private, max-age=10')
        self.write({'templates': templates})

    @staticmethod
    def _get_templates():
        template_ids = []
        try:
            with os.scandir(TEMPLATE_PATH) as it:
                for entry in it:
                    if entry.is_dir() and os.path.isfile(os.path.join(entry.path, 'template.json')):
                        template_ids.append(entry.name)
        except OSError:
            logger.exception('Failed to discover templates:')
            return []
        if not template_ids:
            return []

        templates = []
        for template_id in template_ids:
            try:
                config_path = os.path.join(TEMPLATE_PATH, template_id, 'template.json')
                with open(config_path, encoding='utf-8') as f:
                    cfg = json.load(f)
                if not isinstance(cfg, dict):
                    raise TypeError(f'Config type error, type={type(cfg)}')

                url_str = str(cfg.get('url', ''))
                url = yarl.URL(url_str)
                if not url.absolute:
                    # 相对于模板目录
                    base_url = yarl.URL(f'{TEMPLATE_BASE_URL}/{template_id}/')
                    url = base_url.join(url)
                url_str = str(url)

                template = {
                    'id': template_id,
                    'name': str(cfg.get('name', '')),
                    'version': str(cfg.get('version', '')),
                    'author': str(cfg.get('author', '')),
                    'description': str(cfg.get('description', '')),
                    'url': url_str,
                }
                templates.append(template)
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                logger.exception('template_id=%s failed to load config:', template_id)
        return templates


class NoCacheStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header('Cache-Control', 'no-cache')


ROUTES = [
    (r'/api/server_info', ServerInfoHandler),
    (r'/api/endpoints', ServiceDiscoveryHandler),
    (r'/api/ping', PingHandler),
    (r'/api/emoticon', UploadEmoticonHandler),
    (r'/api/templates', TemplatesHandler),
]
# 通配的放在最后
LAST_ROUTES = [
    (rf'{EMOTICON_BASE_URL}/(.*)', tornado.web.StaticFileHandler, {'path': EMOTICON_UPLOAD_PATH}),
    # 这个目录不保证文件内容不会变，还是不用缓存了
    (r'/custom_public/(.*)', NoCacheStaticFileHandler, {'path': CUSTOM_PUBLIC_PATH}),
    (r'/(.*)', StaticHandler, {'path': config.WEB_ROOT}),
]
