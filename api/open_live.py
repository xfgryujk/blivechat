# -*- coding: utf-8 -*-
import asyncio
import datetime
import hashlib
import hmac
import json
import logging
import random
import re
from typing import *

import aiohttp
import cachetools
import tornado.web

import api.base
import config
import utils.request

logger = logging.getLogger(__name__)

START_GAME_OPEN_LIVE_URL = 'https://live-open.biliapi.com/v2/app/start'
END_GAME_OPEN_LIVE_URL = 'https://live-open.biliapi.com/v2/app/end'
GAME_HEARTBEAT_OPEN_LIVE_URL = 'https://live-open.biliapi.com/v2/app/heartbeat'

COMMON_SERVER_BASE_URL = 'https://chat.bilisc.com'
START_GAME_COMMON_SERVER_URL = COMMON_SERVER_BASE_URL + '/api/internal/open_live/start_game'
END_GAME_COMMON_SERVER_URL = COMMON_SERVER_BASE_URL + '/api/internal/open_live/end_game'
GAME_HEARTBEAT_COMMON_SERVER_URL = COMMON_SERVER_BASE_URL + '/api/internal/open_live/game_heartbeat'

_error_auth_code_cache = cachetools.LRUCache(256)


class TransportError(Exception):
    """网络错误或HTTP状态码错误"""


class BusinessError(Exception):
    """业务返回码错误"""
    def __init__(self, data: dict):
        super().__init__(f"code={data['code']}, message={data['message']}, request_id={data['request_id']}")
        self.data = data

    @property
    def code(self) -> int:
        return self.data['code']


async def request_open_live_or_common_server(open_live_url, common_server_url, body: dict) -> dict:
    """如果配置了开放平台，则直接请求，否则转发请求到公共服务器的内部接口"""
    cfg = config.get_config()
    if cfg.is_open_live_configured:
        return await _request_open_live(open_live_url, body)

    try:
        req_ctx_mgr = utils.request.http_session.post(common_server_url, json=body)
        return await _read_response(req_ctx_mgr)
    except TransportError:
        logger.exception('Request common server failed:')
        raise
    except BusinessError as e:
        logger.warning('Request common server failed: %s', e)
        raise


async def _request_open_live(url, body: dict) -> dict:
    cfg = config.get_config()
    assert cfg.is_open_live_configured

    # 输错身份码的人太多了，屏蔽掉明显错误的请求，防止B站抱怨
    if url == START_GAME_OPEN_LIVE_URL:
        auth_code = body.get('code', '')
        _validate_auth_code(auth_code)
    else:
        auth_code = ''

    body_bytes = json.dumps(body).encode('utf-8')
    headers = {
        'x-bili-accesskeyid': cfg.open_live_access_key_id,
        'x-bili-content-md5': hashlib.md5(body_bytes).hexdigest(),
        'x-bili-signature-method': 'HMAC-SHA256',
        'x-bili-signature-nonce': str(random.randint(0, 999999999)),
        'x-bili-signature-version': '1.0',
        'x-bili-timestamp': str(int(datetime.datetime.now().timestamp())),
    }

    str_to_sign = '\n'.join(
        f'{key}:{value}'
        for key, value in headers.items()
    )
    signature = hmac.new(
        cfg.open_live_access_key_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256
    ).hexdigest()
    headers['Authorization'] = signature

    headers['Content-Type'] = 'application/json'
    headers['Accept'] = 'application/json'

    try:
        req_ctx_mgr = utils.request.http_session.post(url, headers=headers, data=body_bytes)
        return await _read_response(req_ctx_mgr)
    except TransportError:
        logger.exception('Request open live failed:')
        raise
    except BusinessError as e:
        logger.warning('Request open live failed: %s', e)
        if e.code == 7007:
            _error_auth_code_cache[auth_code] = True
        raise


async def _read_response(req_ctx_mgr: AsyncContextManager[aiohttp.ClientResponse]) -> dict:
    try:
        async with req_ctx_mgr as r:
            r.raise_for_status()
            data = await r.json()
            code = data['code']
            if code != 0:
                raise BusinessError(data)
            return data
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        raise TransportError(f'{type(e).__name__}: {e}')


def _validate_auth_code(auth_code):
    if (
        auth_code in _error_auth_code_cache
        # 我也不知道是不是一定是这个格式，先这么处理
        or not re.fullmatch(r'[0-9A-Z]{12,14}', auth_code)
    ):
        raise BusinessError({
            'code': 7007,
            'message': 'oi！oi！oi！你的身份码错误了！别再重试了！！！！！！！！！！',
            'request_id': '0',
            'data': None
        })


class _OpenLiveHandlerBase(api.base.ApiHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.res: Optional[dict] = None

    def prepare(self):
        super().prepare()
        if not isinstance(self.json_args, dict):
            raise tornado.web.MissingArgumentError('body')

        if 'app_id' in self.json_args:
            cfg = config.get_config()
            self.json_args['app_id'] = cfg.open_live_app_id

        logger.info('client=%s requesting open live, cls=%s', self.request.remote_ip, type(self).__name__)


class _PublicHandlerBase(_OpenLiveHandlerBase):
    """外部接口，如果配置了开放平台，则直接请求，否则转发请求到公共服务器的内部接口"""
    _OPEN_LIVE_URL: str
    _COMMON_SERVER_URL: str

    async def post(self):
        try:
            self.res = await request_open_live_or_common_server(
                self._OPEN_LIVE_URL, self._COMMON_SERVER_URL, self.json_args
            )
        except TransportError:
            raise tornado.web.HTTPError(500)
        except BusinessError as e:
            self.res = e.data
        self.write(self.res)


class _PrivateHandlerBase(_OpenLiveHandlerBase):
    """内部接口，如果配置了开放平台，则直接请求，否则响应错误"""
    _OPEN_LIVE_URL: str

    async def post(self):
        cfg = config.get_config()
        if not cfg.is_open_live_configured:
            raise tornado.web.HTTPError(501)

        try:
            self.res = await _request_open_live(self._OPEN_LIVE_URL, self.json_args)
        except TransportError:
            raise tornado.web.HTTPError(500)
        except BusinessError as e:
            self.res = e.data
        self.write(self.res)


class _StartGameMixin(_OpenLiveHandlerBase):
    _OPEN_LIVE_URL = START_GAME_OPEN_LIVE_URL
    _COMMON_SERVER_URL = START_GAME_COMMON_SERVER_URL

    async def post(self):
        await super().post()  # noqa
        if self.res is None:
            return

        try:
            room_id = self.res['data']['anchor_info']['room_id']
        except (TypeError, KeyError):
            room_id = None
        code = self.res['code']
        logger.info('room_id=%s start game res: %s %s', room_id, code, self.res['message'])
        if code == 7007:
            # 身份码错误
            # 让我看看是哪个混蛋把房间ID、UID当做身份码
            logger.info('Auth code error! auth_code=%s', self.json_args.get('code', None))


class StartGamePublicHandler(_StartGameMixin, _PublicHandlerBase):
    pass


class StartGamePrivateHandler(_StartGameMixin, _PrivateHandlerBase):
    pass


class EndGamePublicHandler(_PublicHandlerBase):
    _OPEN_LIVE_URL = END_GAME_OPEN_LIVE_URL
    _COMMON_SERVER_URL = END_GAME_COMMON_SERVER_URL


class EndGamePrivateHandler(_PrivateHandlerBase):
    _OPEN_LIVE_URL = END_GAME_OPEN_LIVE_URL


class GameHeartbeatPublicHandler(_PublicHandlerBase):
    _OPEN_LIVE_URL = GAME_HEARTBEAT_OPEN_LIVE_URL
    _COMMON_SERVER_URL = GAME_HEARTBEAT_COMMON_SERVER_URL


class GameHeartbeatPrivateHandler(_PrivateHandlerBase):
    _OPEN_LIVE_URL = GAME_HEARTBEAT_OPEN_LIVE_URL


ROUTES = [
    (r'/api/open_live/start_game', StartGamePublicHandler),
    (r'/api/internal/open_live/start_game', StartGamePrivateHandler),
    (r'/api/open_live/end_game', EndGamePublicHandler),
    (r'/api/internal/open_live/end_game', EndGamePrivateHandler),
    (r'/api/open_live/game_heartbeat', GameHeartbeatPublicHandler),
    (r'/api/internal/open_live/game_heartbeat', GameHeartbeatPrivateHandler),
]
