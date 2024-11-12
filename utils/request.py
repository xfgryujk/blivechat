# -*- coding: utf-8 -*-
import asyncio
import datetime
import logging
from typing import *

import aiohttp
import circuitbreaker

import api.open_live
import config
import utils.async_io

logger = logging.getLogger(__name__)

# 不带这堆头部有时候也能成功请求，但是带上后成功的概率更高
BILIBILI_COMMON_HEADERS = {
    'Origin': 'https://www.bilibili.com',
    'Referer': 'https://www.bilibili.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/114.0.0.0 Safari/537.36'
}

http_session: Optional[aiohttp.ClientSession] = None

_COMMON_SERVER_DISCOVERY_URLS = [
    'https://api1.blive.chat/api/endpoints',
    'https://api2.blive.chat/api/endpoints',
]
_last_update_common_server_time: Optional[datetime.datetime] = None
_common_server_base_urls = [
    'https://api1.blive.chat',
    'https://api2.blive.chat',
]
_cur_common_server_base_url: Optional[str] = None
_common_server_base_url_to_circuit_breaker: Dict[str, circuitbreaker.CircuitBreaker] = {}


def init():
    global http_session
    http_session = aiohttp.ClientSession(
        response_class=CustomClientResponse,
        timeout=aiohttp.ClientTimeout(total=10),
    )

    cfg = config.get_config()
    if not cfg.is_open_live_configured:
        _update_common_server_base_urls()


async def shut_down():
    if http_session is not None:
        await http_session.close()


class CustomClientResponse(aiohttp.ClientResponse):
    # 因为aiohttp的BUG，当底层连接断开时，_wait_released可能会抛出CancelledError，导致上层协程结束。这里改个错误类型
    async def _wait_released(self):
        try:
            return await super()._wait_released()
        except asyncio.CancelledError as e:
            raise aiohttp.ClientConnectionError('Connection released') from e


def _update_common_server_base_urls():
    global _last_update_common_server_time
    cur_time = datetime.datetime.now()
    if (
        _last_update_common_server_time is not None
        and cur_time - _last_update_common_server_time < datetime.timedelta(minutes=3)
    ):
        return
    _last_update_common_server_time = cur_time
    utils.async_io.create_task_with_ref(_do_update_common_server_base_urls())


async def _do_update_common_server_base_urls():
    global _last_update_common_server_time
    _last_update_common_server_time = datetime.datetime.now()

    async def request_get_urls(discovery_url):
        async with http_session.get(discovery_url) as res:
            res.raise_for_status()
            data = await res.json()
        return data['endpoints']

    common_server_base_urls = []
    futures = [
        asyncio.create_task(request_get_urls(url))
        for url in _COMMON_SERVER_DISCOVERY_URLS
    ]
    for future in asyncio.as_completed(futures):
        try:
            common_server_base_urls = await future
            break
        except Exception as e:
            logger.warning('Failed to discover common server endpoints from one source: %s', e)
    for future in futures:
        future.cancel()
    if not common_server_base_urls:
        logger.error('Failed to discover common server endpoints from any source')
        return

    # 按响应时间排序
    sorted_common_server_base_urls = []
    error_base_urls = []

    async def test_endpoint(base_url):
        try:
            url = base_url + '/api/ping'
            async with http_session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as res:
                res.raise_for_status()
                sorted_common_server_base_urls.append(base_url)
        except Exception:  # noqa
            error_base_urls.append(base_url)

    await asyncio.gather(*(test_endpoint(base_url) for base_url in common_server_base_urls))
    sorted_common_server_base_urls.extend(error_base_urls)

    global _common_server_base_urls, _cur_common_server_base_url
    _common_server_base_urls = sorted_common_server_base_urls
    if _cur_common_server_base_url not in _common_server_base_urls:
        _cur_common_server_base_url = None
    logger.info('Found common server endpoints: %s', _common_server_base_urls)


def get_common_server_base_url_and_circuit_breaker() -> Tuple[Optional[str], Optional[circuitbreaker.CircuitBreaker]]:
    _update_common_server_base_urls()

    global _cur_common_server_base_url
    if _cur_common_server_base_url is not None:
        breaker = _get_or_add_common_server_circuit_breaker(_cur_common_server_base_url)
        if breaker.state != circuitbreaker.STATE_OPEN:
            return _cur_common_server_base_url, breaker
        _cur_common_server_base_url = None

    # 找第一个未熔断的
    for base_url in _common_server_base_urls:
        breaker = _get_or_add_common_server_circuit_breaker(base_url)
        if breaker.state != circuitbreaker.STATE_OPEN:
            _cur_common_server_base_url = base_url
            logger.info('Switch common server endpoint to %s', _cur_common_server_base_url)
            return _cur_common_server_base_url, breaker

    return None, None


def _get_or_add_common_server_circuit_breaker(base_url):
    breaker = _common_server_base_url_to_circuit_breaker.get(base_url, None)
    if breaker is None:
        breaker = _common_server_base_url_to_circuit_breaker[base_url] = circuitbreaker.CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60,
            expected_exception=api.open_live.TransportError,
        )
    return breaker
