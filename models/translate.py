# -*- coding: utf-8 -*-

import asyncio
import functools
import hashlib
import logging
import random
import re
import time

import yarl
from typing import *

import aiohttp

logger = logging.getLogger(__name__)

NO_TRANSLATE_TEXTS = {
    '草', '草草', '草草草', '草生', '大草原', '上手', '上手上手', '理解', '理解理解', '天才', '天才天才',
    '强', '余裕', '余裕余裕', '大丈夫', '再放送', '放送事故', '清楚', '清楚清楚'
}

_main_event_loop = asyncio.get_event_loop()
_http_session = aiohttp.ClientSession()
_translate_providers: List['TranslateProvider'] = []
# text -> res
_translate_cache: Dict[str, str] = {}
# 正在翻译的Future，text -> Future
_text_future_map: Dict[str, asyncio.Future] = {}


def init():
    asyncio.ensure_future(_do_init())


async def _do_init():
    # 考虑优先级
    providers = [
        TencentTranslate(),
        YoudaoTranslate(),
        BilibiliTranslate()
    ]
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
    if text.startswith('【'):
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


class TencentTranslate(TranslateProvider):
    def __init__(self):
        # 过期时间1小时
        self._qtv = ''
        self._qtk = ''
        self._reinit_future = None
        # 连续失败的次数
        self._fail_count = 0
        self._cool_down_future = None

    async def init(self):
        self._reinit_future = asyncio.ensure_future(self._reinit_coroutine())
        return await self._do_init()

    async def _do_init(self):
        try:
            async with _http_session.get('https://fanyi.qq.com/') as r:
                if r.status != 200:
                    logger.warning('TencentTranslate init request failed: status=%d %s', r.status, r.reason)
                    return False
                html = await r.text()

            m = re.search(r"""\breauthuri\s*=\s*['"](.+?)['"]""", html)
            if m is None:
                logger.exception('TencentTranslate init failed: reauthuri not found')
                return False
            reauthuri = m[1]

            async with _http_session.post('https://fanyi.qq.com/api/' + reauthuri) as r:
                if r.status != 200:
                    logger.warning('TencentTranslate init request failed: status=%d %s', r.status, r.reason)
                    return False
                data = await r.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            logger.exception('TencentTranslate init error:')
            return False

        qtv = data.get('qtv', None)
        if qtv is None:
            logger.warning('TencentTranslate init failed: qtv not found')
            return False
        qtk = data.get('qtk', None)
        if qtk is None:
            logger.warning('TencentTranslate init failed: qtk not found')
            return False

        self._qtv = qtv
        self._qtk = qtk
        return True

    async def _reinit_coroutine(self):
        try:
            while True:
                await asyncio.sleep(30)
                while True:
                    logger.debug('TencentTranslate reinit')
                    try:
                        if await self._do_init():
                            break
                    except Exception:
                        logger.exception('TencentTranslate init error:')
                    await asyncio.sleep(3 * 60)
        except asyncio.CancelledError:
            pass

    @property
    def is_available(self):
        return self._qtv != '' and self._qtk != ''

    def translate(self, text, future):
        asyncio.ensure_future(self._translate_coroutine(text, future))

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
                    'source': 'zh',
                    'target': 'jp',
                    'sourceText': text,
                    'qtv': self._qtv,
                    'qtk': self._qtk
                }
            ) as r:
                if r.status != 200:
                    logger.warning('TencentTranslate request failed: status=%d %s', r.status, r.reason)
                    return None
                data = await r.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            return None
        if data['errCode'] != 0:
            logger.warning('TencentTranslate failed: %d %s', data['errCode'], data['errMsg'])
            return None
        res = ''.join(record['targetText'] for record in data['translate']['records'])
        if res == '' and text.strip() != '':
            # qtv、qtk过期
            logger.warning('TencentTranslate result is empty %s', data)
            return None
        return res

    def _on_fail(self):
        self._fail_count += 1
        # 目前没有测试出被ban的情况，为了可靠性，连续失败20次时冷却并重新init
        if self._fail_count >= 20 and self._cool_down_future is None:
            self._cool_down_future = asyncio.ensure_future(self._cool_down())

    async def _cool_down(self):
        logger.info('TencentTranslate is cooling down')
        self._qtv = self._qtk = ''
        try:
            while True:
                await asyncio.sleep(3 * 60)
                logger.info('TencentTranslate reinit')
                try:
                    if await self._do_init():
                        self._fail_count = 0
                        break
                except Exception:
                    logger.exception('TencentTranslate init error:')
        finally:
            logger.info('TencentTranslate finished cooling down')
            self._cool_down_future = None


class YoudaoTranslate(TranslateProvider):
    def __init__(self):
        self._has_init = False
        self._cool_down_future = None

    async def init(self):
        # 获取cookie
        try:
            async with _http_session.get('http://fanyi.youdao.com/') as r:
                if r.status >= 400:
                    logger.warning('YoudaoTranslate init request failed: status=%d %s', r.status, r.reason)
                    return False
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            return False

        cookies = _http_session.cookie_jar.filter_cookies(yarl.URL('http://fanyi.youdao.com/'))
        res = 'JSESSIONID' in cookies and 'OUTFOX_SEARCH_USER_ID' in cookies
        if res:
            self._has_init = True
        return res

    @property
    def is_available(self):
        return self._has_init

    def translate(self, text, future):
        asyncio.ensure_future(self._translate_coroutine(text, future))

    async def _translate_coroutine(self, text, future):
        try:
            res = await self._do_translate(text)
        except BaseException as e:
            future.set_exception(e)
        else:
            future.set_result(res)

    async def _do_translate(self, text):
        try:
            async with _http_session.post(
                'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule',
                headers={
                    'Referer': 'http://fanyi.youdao.com/'
                },
                data={
                    'i': text,
                    'from': 'zh-CHS',
                    'to': 'ja',
                    'smartresult': 'dict',
                    'client': 'fanyideskweb',
                    **self._generate_salt(text),
                    'doctype': 'json',
                    'version': '2.1',
                    'keyfrom': 'fanyi.web',
                    'action': 'FY_BY_REALTlME'
                }
            ) as r:
                if r.status != 200:
                    logger.warning('YoudaoTranslate request failed: status=%d %s', r.status, r.reason)
                    return None
                data = await r.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            return None
        except aiohttp.ContentTypeError:
            # 被ban了
            if self._cool_down_future is None:
                self._cool_down_future = asyncio.ensure_future(self._cool_down())
            return None
        if data['errorCode'] != 0:
            logger.warning('YoudaoTranslate failed: %d', data['errorCode'])
            return None

        res = []
        for outer_result in data['translateResult']:
            for inner_result in outer_result:
                res.append(inner_result['tgt'])
        return ''.join(res)

    @staticmethod
    def _generate_salt(text):
        timestamp = int(time.time() * 1000)
        salt = f'{timestamp}{random.randint(0, 9)}'
        md5 = hashlib.md5()
        md5.update(f'fanyideskweb{text}{salt}n%A-rKaT5fb[Gy?;N5@Tj'.encode())
        sign = md5.hexdigest()
        return {
            'ts': timestamp,
            'bv': '7bcd9ea3ff9b319782c2a557acee9179',  # md5(navigator.appVersion)
            'salt': salt,
            'sign': sign
        }

    async def _cool_down(self):
        logger.info('YoudaoTranslate is cooling down')
        self._has_init = False
        try:
            while True:
                await asyncio.sleep(3 * 60)
                try:
                    is_success = await self.init()
                except Exception:
                    logger.exception('YoudaoTranslate init error:')
                    continue
                if is_success:
                    break
        finally:
            logger.info('YoudaoTranslate finished cooling down')
            self._cool_down_future = None


# 目前B站后端是百度翻译
class BilibiliTranslate(TranslateProvider):
    def __init__(self):
        # 最长等待时间大约21秒，(text, future)
        self._text_queue = asyncio.Queue(7)

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
                # 频率限制一分钟20次
                await asyncio.sleep(3.1)
            except Exception:
                logger.exception('BilibiliTranslate error:')

    async def _translate_coroutine(self, text, future):
        try:
            res = await self._do_translate(text)
        except BaseException as e:
            future.set_exception(e)
        else:
            future.set_result(res)

    @staticmethod
    async def _do_translate(text):
        try:
            async with _http_session.get(
                'https://api.live.bilibili.com/av/v1/SuperChat/messageTranslate',
                params={
                    'parent_area_id': '1',
                    'area_id': '199',
                    'msg': text
                }
            ) as r:
                if r.status != 200:
                    logger.warning('BilibiliTranslate request failed: status=%d %s', r.status, r.reason)
                    return None
                data = await r.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            return None
        if data['code'] != 0:
            logger.warning('BilibiliTranslate failed: %d %s', data['code'], data['msg'])
            return None
        return data['data']['message_trans']
