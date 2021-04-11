# -*- coding: utf-8 -*-

import asyncio
import functools
import logging
import re
from typing import *

import aiohttp

import config

logger = logging.getLogger(__name__)

NO_TRANSLATE_TEXTS = {
    '草', '草草', '草草草', '草生', '大草原', '上手', '上手上手', '理解', '理解理解', '天才', '天才天才',
    '强', '余裕', '余裕余裕', '大丈夫', '再放送', '放送事故', '清楚', '清楚清楚'
}

_main_event_loop = asyncio.get_event_loop()
_http_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
_translate_providers: List['TranslateProvider'] = []
# text -> res
_translate_cache: Dict[str, str] = {}
# 正在翻译的Future，text -> Future
_text_future_map: Dict[str, asyncio.Future] = {}


def init():
    asyncio.ensure_future(_do_init())


async def _do_init():
    cfg = config.get_config()
    providers = []
    for trans_cfg in cfg.translator_configs:
        provider = None
        type_ = trans_cfg['type']

        if type_ == 'TencentTranslateFree':
            provider = TencentTranslateFree(
                trans_cfg['query_interval'], trans_cfg['max_queue_size'], trans_cfg['source_language'],
                trans_cfg['target_language']
            )
        elif type_ == 'BilibiliTranslateFree':
            provider = BilibiliTranslateFree(trans_cfg['query_interval'], trans_cfg['max_queue_size'])

        if provider is not None:
            providers.append(provider)
    await asyncio.gather(*(provider.init() for provider in providers))
    global _translate_providers
    _translate_providers = providers


def need_translate(text):
    text = text.strip()
    # 没有中文，平时打不出的字不管
    if not any(0x4E00 <= ord(c) <= 0x9FFF for c in text):
        return False
    # 含有日文假名
    if any(0x3040 <= ord(c) <= 0x30FF for c in text):
        return False
    # 弹幕同传
    if '【' in text:
        return False
    # 中日双语
    if text in NO_TRANSLATE_TEXTS:
        return False
    return True


def get_translation_from_cache(text):
    key = text.strip().lower()
    return _translate_cache.get(key, None)


def translate(text) -> Awaitable[Optional[str]]:
    key = text.strip().lower()
    # 如果已有正在翻译的future则返回，防止重复翻译
    future = _text_future_map.get(key, None)
    if future is not None:
        return future
    # 否则创建一个翻译任务
    future = _main_event_loop.create_future()

    # 查缓存
    res = _translate_cache.get(key, None)
    if res is not None:
        future.set_result(res)
        return future

    for provider in _translate_providers:
        if provider.is_available:
            _text_future_map[key] = future
            future.add_done_callback(functools.partial(_on_translate_done, key))
            provider.translate(text, future)
            return future

    future.set_result(None)
    return future


def _on_translate_done(key, future):
    _text_future_map.pop(key, None)
    # 缓存
    try:
        res = future.result()
    except Exception:
        return
    if res is None:
        return
    _translate_cache[key] = res
    while len(_translate_cache) > 50000:
        _translate_cache.pop(next(iter(_translate_cache)), None)


class TranslateProvider:
    async def init(self):
        return True

    @property
    def is_available(self):
        return True

    def translate(self, text, future):
        raise NotImplementedError


class FlowControlTranslateProvider(TranslateProvider):
    def __init__(self, query_interval, max_queue_size):
        self._query_interval = query_interval
        # (text, future)
        self._text_queue = asyncio.Queue(max_queue_size)

    async def init(self):
        asyncio.ensure_future(self._translate_consumer())
        return True

    @property
    def is_available(self):
        return not self._text_queue.full()

    def translate(self, text, future):
        try:
            self._text_queue.put_nowait((text, future))
        except asyncio.QueueFull:
            future.set_result(None)

    async def _translate_consumer(self):
        while True:
            try:
                text, future = await self._text_queue.get()
                asyncio.ensure_future(self._translate_coroutine(text, future))
                # 频率限制
                await asyncio.sleep(self._query_interval)
            except Exception:
                logger.exception('FlowControlTranslateProvider error:')

    async def _translate_coroutine(self, text, future):
        try:
            res = await self._do_translate(text)
        except BaseException as e:
            future.set_exception(e)
        else:
            future.set_result(res)

    async def _do_translate(self, text):
        raise NotImplementedError


class TencentTranslateFree(FlowControlTranslateProvider):
    def __init__(self, query_interval, max_queue_size, source_language, target_language):
        super().__init__(query_interval, max_queue_size)
        self._source_language = source_language
        self._target_language = target_language

        self._qtv = ''
        self._qtk = ''
        self._reinit_future = None
        # 连续失败的次数
        self._fail_count = 0

    async def init(self):
        if not await super().init():
            return False
        if not await self._do_init():
            return False
        self._reinit_future = asyncio.ensure_future(self._reinit_coroutine())
        return True

    async def _do_init(self):
        try:
            async with _http_session.get('https://fanyi.qq.com/') as r:
                if r.status != 200:
                    logger.warning('TencentTranslateFree init request failed: status=%d %s', r.status, r.reason)
                    return False
                html = await r.text()

            m = re.search(r"""\breauthuri\s*=\s*['"](.+?)['"]""", html)
            if m is None:
                logger.exception('TencentTranslateFree init failed: reauthuri not found')
                return False
            reauthuri = m[1]

            async with _http_session.post('https://fanyi.qq.com/api/' + reauthuri) as r:
                if r.status != 200:
                    logger.warning('TencentTranslateFree init request failed: reauthuri=%s, status=%d %s',
                                   reauthuri, r.status, r.reason)
                    return False
                data = await r.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            logger.exception('TencentTranslateFree init error:')
            return False

        qtv = data.get('qtv', None)
        if qtv is None:
            logger.warning('TencentTranslateFree init failed: qtv not found')
            return False
        qtk = data.get('qtk', None)
        if qtk is None:
            logger.warning('TencentTranslateFree init failed: qtk not found')
            return False

        self._qtv = qtv
        self._qtk = qtk
        return True

    async def _reinit_coroutine(self):
        try:
            while True:
                await asyncio.sleep(30)
                logger.debug('TencentTranslateFree reinit')
                asyncio.ensure_future(self._do_init())
        except asyncio.CancelledError:
            pass

    @property
    def is_available(self):
        return self._qtv != '' and self._qtk != '' and super().is_available

    async def _translate_coroutine(self, text, future):
        try:
            res = await self._do_translate(text)
        except BaseException as e:
            future.set_exception(e)
            self._on_fail()
            return
        future.set_result(res)
        if res is None:
            self._on_fail()
        else:
            self._fail_count = 0

    async def _do_translate(self, text):
        try:
            async with _http_session.post(
                'https://fanyi.qq.com/api/translate',
                headers={
                    'Referer': 'https://fanyi.qq.com/'
                },
                data={
                    'source': self._source_language,
                    'target': self._target_language,
                    'sourceText': text,
                    'qtv': self._qtv,
                    'qtk': self._qtk
                }
            ) as r:
                if r.status != 200:
                    logger.warning('TencentTranslateFree request failed: status=%d %s', r.status, r.reason)
                    return None
                data = await r.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            return None
        if data['errCode'] != 0:
            logger.warning('TencentTranslateFree failed: %d %s', data['errCode'], data['errMsg'])
            return None
        res = ''.join(record['targetText'] for record in data['translate']['records'])
        if res == '' and text.strip() != '':
            # qtv、qtk过期
            logger.warning('TencentTranslateFree result is empty %s', data)
            return None
        return res

    def _on_fail(self):
        self._fail_count += 1
        # 目前没有测试出被ban的情况，为了可靠性，连续失败20次时冷却直到下次重新init
        if self._fail_count >= 20:
            self._cool_down()

    def _cool_down(self):
        logger.info('TencentTranslateFree is cooling down')
        # 下次_do_init后恢复
        self._qtv = self._qtk = ''
        self._fail_count = 0


class BilibiliTranslateFree(FlowControlTranslateProvider):
    def __init__(self, query_interval, max_queue_size):
        super().__init__(query_interval, max_queue_size)

    async def _do_translate(self, text):
        try:
            async with _http_session.get(
                'https://api.live.bilibili.com/av/v1/SuperChat/messageTranslate',
                params={
                    'room_id': '21396545',
                    'ruid': '407106379',
                    'parent_area_id': '9',
                    'area_id': '371',
                    'msg': text
                }
            ) as r:
                if r.status != 200:
                    logger.warning('BilibiliTranslateFree request failed: status=%d %s', r.status, r.reason)
                    return None
                data = await r.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            return None
        if data['code'] != 0:
            logger.warning('BilibiliTranslateFree failed: %d %s', data['code'], data['msg'])
            return None
        return data['data']['message_trans']
