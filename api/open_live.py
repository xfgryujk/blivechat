# -*- coding: utf-8 -*-
import asyncio
import datetime
import hashlib
import hmac
import json
import logging
import re
import uuid
from typing import *

import aiohttp
import cachetools
import tornado.web

import api.base
import config
import services.open_live
import utils.rate_limit
import utils.request

logger = logging.getLogger(__name__)

OPEN_LIVE_BASE_URL = 'https://live-open.biliapi.com'
START_GAME_OPEN_LIVE_URL = OPEN_LIVE_BASE_URL + '/v2/app/start'
END_GAME_OPEN_LIVE_URL = OPEN_LIVE_BASE_URL + '/v2/app/end'
GAME_HEARTBEAT_OPEN_LIVE_URL = OPEN_LIVE_BASE_URL + '/v2/app/heartbeat'
GAME_BATCH_HEARTBEAT_OPEN_LIVE_URL = OPEN_LIVE_BASE_URL + '/v2/app/batchHeartbeat'

COMMON_SERVER_BASE_URL = 'https://chat.bilisc.com'
START_GAME_COMMON_SERVER_URL = COMMON_SERVER_BASE_URL + '/api/internal/open_live/start_game'
END_GAME_COMMON_SERVER_URL = COMMON_SERVER_BASE_URL + '/api/internal/open_live/end_game'
GAME_HEARTBEAT_COMMON_SERVER_URL = COMMON_SERVER_BASE_URL + '/api/internal/open_live/game_heartbeat'

_error_auth_code_cache = cachetools.LRUCache(256)
# 应B站要求，抓一下刷请求的人，不会用于其他用途
auth_code_room_id_cache = cachetools.LRUCache(256)
# 用于限制请求开放平台的频率
_open_live_rate_limiter = utils.rate_limit.TokenBucket(8, 8)


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
        return await request_open_live(open_live_url, body)

    try:
        req_ctx_mgr = utils.request.http_session.post(common_server_url, json=body)
        return await _read_response(req_ctx_mgr)
    except TransportError:
        logger.exception('Request common server failed:')
        raise
    except BusinessError as e:
        logger.warning('Request common server failed: %s', e)
        raise


async def request_open_live(url, body: dict, *, ignore_rate_limit=False) -> dict:
    cfg = config.get_config()
    assert cfg.is_open_live_configured

    # 输错身份码的人太多了，屏蔽掉明显错误的请求，防止B站抱怨
    if url == START_GAME_OPEN_LIVE_URL:
        auth_code = body.get('code', '')
        _validate_auth_code(auth_code)
    else:
        auth_code = ''

    # 频率限制，防止触发B站风控被下架
    if not _open_live_rate_limiter.try_decrease_token() and not ignore_rate_limit:
        raise BusinessError({'code': 4009, 'message': 'BLC接口访问限制', 'request_id': '0', 'data': None})

    body_bytes = json.dumps(body).encode('utf-8')
    headers = {
        'x-bili-accesskeyid': cfg.open_live_access_key_id,
        'x-bili-content-md5': hashlib.md5(body_bytes).hexdigest(),
        'x-bili-signature-method': 'HMAC-SHA256',
        'x-bili-signature-nonce': uuid.uuid4().hex,
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
        msg = str(e)
        if e.code == 7010:
            # 新版本日志可以截断，避免日志太长了
            msg = msg[:30] + '...'
        logger.warning('Request open live failed: %s', msg)

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
                if code == 7010:
                    data['message'] += (
                        '  解决方法：https://github.com/xfgryujk/blivechat/wiki/%E6%B3%A8%E6%84%8F%E4%BA%8B%E9%A1%B9%E5'
                        '%92%8C%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98#%E6%8A%A5%E9%94%997010-%E8%B6%85%E8%BF%87%E4%B8%8'
                        'A%E9%99%90%E5%90%8C%E4%B8%80%E4%B8%AA%E5%BA%94%E7%94%A8%E5%8D%95%E4%B8%AA%E7%9B%B4%E6%92%AD%'
                        'E9%97%B4%E6%9C%80%E5%A4%9A%E5%90%8C%E6%97%B6%E6%89%93%E5%BC%805%E4%B8%AA'
                    )
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
            'message': 'CNM！你的身份码错误了！别再重试了！！！！！！！！！！',
            'request_id': '0',
            'data': None
        })


class _OpenLiveHandlerBase(api.base.ApiHandler):
    _LOG_REQUEST = True

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

        if self._LOG_REQUEST:
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
            self.res = await request_open_live(self._OPEN_LIVE_URL, self.json_args)
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

        auth_code = self.json_args.get('code', None)
        try:
            room_id = self.res['data']['anchor_info']['room_id']
        except (TypeError, KeyError):
            room_id = auth_code_room_id_cache.get(auth_code, None)
        else:
            auth_code_room_id_cache[auth_code] = room_id
        try:
            game_id = self.res['data']['game_info']['game_id']
        except (TypeError, KeyError):
            game_id = None

        code = self.res['code']
        msg = self.res['message']
        if code == 7010:
            # 新版本日志可以截断，避免日志太长了
            msg = msg[:10] + '...'
        logger.info(
            'client=%s room_id=%s start game res: %s %s, game_id=%s', self.request.remote_ip, room_id,
            code, msg, game_id
        )
        if code == 7007:
            # 身份码错误
            # 让我看看是哪个混蛋把房间ID、UID当做身份码
            logger.info('client=%s auth code error! auth_code=%s', self.request.remote_ip, auth_code)


class StartGamePublicHandler(_StartGameMixin, _PublicHandlerBase):
    pass


class StartGamePrivateHandler(_StartGameMixin, _PrivateHandlerBase):
    pass


class EndGamePublicHandler(_PublicHandlerBase):
    _OPEN_LIVE_URL = END_GAME_OPEN_LIVE_URL
    _COMMON_SERVER_URL = END_GAME_COMMON_SERVER_URL


class EndGamePrivateHandler(_PrivateHandlerBase):
    _OPEN_LIVE_URL = END_GAME_OPEN_LIVE_URL


class GameHeartbeatPublicHandler(_OpenLiveHandlerBase):
    _LOG_REQUEST = False

    async def post(self):
        game_id = self.json_args.get('game_id', None)
        if not isinstance(game_id, str) or game_id == '':
            raise tornado.web.MissingArgumentError('game_id')

        try:
            self.res = await send_game_heartbeat_by_service_or_common_server(game_id)
        except TransportError as e:
            logger.error(
                'client=%s game heartbeat failed, game_id=%s, error: %s', self.request.remote_ip, game_id, e
            )
            raise tornado.web.HTTPError(500)
        except BusinessError as e:
            logger.info(
                'client=%s game heartbeat failed, game_id=%s, error: %s', self.request.remote_ip, game_id, e
            )
            self.res = e.data
        self.write(self.res)


async def send_game_heartbeat_by_service_or_common_server(game_id):
    cfg = config.get_config()
    if cfg.is_open_live_configured:
        return await services.open_live.send_game_heartbeat(game_id)
    # 这里GAME_HEARTBEAT_OPEN_LIVE_URL没用，因为一定是请求公共服务器
    return await request_open_live_or_common_server(
        GAME_HEARTBEAT_OPEN_LIVE_URL, GAME_HEARTBEAT_COMMON_SERVER_URL, {'game_id': game_id}
    )


class GameHeartbeatPrivateHandler(_OpenLiveHandlerBase):
    _LOG_REQUEST = False

    async def post(self):
        cfg = config.get_config()
        if not cfg.is_open_live_configured:
            raise tornado.web.HTTPError(501)

        game_id = self.json_args.get('game_id', None)
        if not isinstance(game_id, str) or game_id == '':
            raise tornado.web.MissingArgumentError('game_id')

        try:
            self.res = await services.open_live.send_game_heartbeat(game_id)
        except TransportError as e:
            logger.error(
                'client=%s game heartbeat failed, game_id=%s, error: %s', self.request.remote_ip, game_id, e
            )
            raise tornado.web.HTTPError(500)
        except BusinessError as e:
            logger.info(
                'client=%s game heartbeat failed, game_id=%s, error: %s', self.request.remote_ip, game_id, e
            )
            self.res = e.data
        self.write(self.res)


ROUTES = [
    (r'/api/open_live/start_game', StartGamePublicHandler),
    (r'/api/internal/open_live/start_game', StartGamePrivateHandler),
    (r'/api/open_live/end_game', EndGamePublicHandler),
    (r'/api/internal/open_live/end_game', EndGamePrivateHandler),
    (r'/api/open_live/game_heartbeat', GameHeartbeatPublicHandler),
    (r'/api/internal/open_live/game_heartbeat', GameHeartbeatPrivateHandler),
]
