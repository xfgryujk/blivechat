# -*- coding: utf-8 -*-
import asyncio
import base64
import dataclasses
import datetime
import enum
import functools
import hashlib
import hmac
import json
import logging
import random
import re
from typing import *

import Crypto.Cipher.AES as cry_aes  # noqa
import Crypto.Util.Padding as cry_pad  # noqa
import aiohttp
import cachetools

import config
import utils.async_io
import utils.request

logger = logging.getLogger(__name__)

NO_TRANSLATE_TEXTS = {
    '草', '草草', '草草草', '草生', '大草原', '上手', '上手上手', '理解', '理解理解', '天才', '天才天才',
    '强', '余裕', '余裕余裕', '大丈夫', '再放送', '放送事故', '清楚', '清楚清楚'
}

_translate_providers: List['TranslateProvider'] = []
# text -> res
_translate_cache: Optional[cachetools.LRUCache] = None
# 正在翻译的Future，text -> Future
_text_future_map: Dict[str, asyncio.Future] = {}
# 正在翻译的任务队列，索引是优先级
_task_queues: List['asyncio.Queue[TranslateTask]'] = []


class Priority(enum.IntEnum):
    HIGH = 0
    NORMAL = 1


@dataclasses.dataclass
class TranslateTask:
    priority: Priority
    text: str
    future: 'asyncio.Future[Optional[str]]'
    remain_retry_count: int


def init():
    cfg = config.get_config()
    global _translate_cache, _task_queues
    _translate_cache = cachetools.LRUCache(cfg.translation_cache_size)
    # 总队列长度会超过translate_max_queue_size，不用这么严格
    _task_queues = [asyncio.Queue(cfg.translate_max_queue_size) for _ in range(len(Priority))]
    utils.async_io.create_task_with_ref(_do_init())


async def _do_init():
    cfg = config.get_config()
    if not cfg.enable_translate:
        return
    providers = []
    for trans_cfg in cfg.translator_configs:
        provider = create_translate_provider(trans_cfg)
        if provider is not None:
            providers.append(provider)
    await asyncio.gather(*(provider.init() for provider in providers))
    global _translate_providers
    _translate_providers = providers


def create_translate_provider(cfg):
    type_ = cfg['type']
    if type_ == 'TencentTranslateFree':
        return TencentTranslateFree(
            cfg['query_interval'], cfg['source_language'], cfg['target_language']
        )
    elif type_ == 'TencentTranslate':
        return TencentTranslate(
            cfg['query_interval'], cfg['source_language'], cfg['target_language'],
            cfg['secret_id'], cfg['secret_key'], cfg['region']
        )
    elif type_ == 'BaiduTranslate':
        return BaiduTranslate(
            cfg['query_interval'], cfg['source_language'], cfg['target_language'],
            cfg['app_id'], cfg['secret']
        )
    elif type_ == 'GeminiTranslate':
        return GeminiTranslate(            
            cfg['query_interval'], cfg['proxy'], cfg['api_key'], cfg['model_code'],
            cfg['prompt'], cfg['temperature']
        )
    return None


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


def translate(text, priority=Priority.NORMAL) -> Awaitable[Optional[str]]:
    key = text.strip().lower()
    # 如果已有正在翻译的future则返回，防止重复翻译
    future = _text_future_map.get(key, None)
    if future is not None:
        return future
    # 否则创建一个翻译任务
    future = asyncio.get_running_loop().create_future()

    # 查缓存
    res = _translate_cache.get(key, None)
    if res is not None:
        future.set_result(res)
        return future

    task = TranslateTask(
        priority=priority,
        text=text,
        future=future,
        remain_retry_count=3 if priority == Priority.HIGH else 1
    )
    if not _push_task(task):
        future.set_result(None)
        return future

    _text_future_map[key] = future
    future.add_done_callback(functools.partial(_on_translate_done, key))
    return future


def _on_translate_done(key, future):
    _text_future_map.pop(key, None)
    # 缓存
    try:
        res = future.result()
    except Exception:  # noqa
        return
    if res is None:
        return
    _translate_cache[key] = res


def _push_task(task: TranslateTask):
    if not _has_available_translate_provider():
        return False

    queue = _task_queues[task.priority]
    if not queue.full():
        queue.put_nowait(task)
        return True

    if task.priority != Priority.HIGH:
        return False

    # 高优先级的尝试降级，挤掉低优先级的任务
    queue = _task_queues[Priority.NORMAL]
    if queue.full():
        lower_task = queue.get_nowait()
        lower_task.future.set_result(None)
    queue.put_nowait(task)
    return True


async def _pop_task() -> TranslateTask:
    # 按优先级遍历，看是否已经有任务
    for queue in _task_queues:
        if not queue.empty():
            return queue.get_nowait()

    done_future_set, pending_future_set = await asyncio.wait(
        [asyncio.create_task(queue.get()) for queue in _task_queues],
        return_when=asyncio.FIRST_COMPLETED
    )
    for future in pending_future_set:
        future.cancel()

    # 如果有多个队列都取到任务了，只返回优先级最高的那一个，剩下的放回队列
    assert len(done_future_set) != 0
    tasks = [await future for future in done_future_set]
    if len(tasks) > 1:
        tasks.sort(key=lambda task_: task_.priority)

    res = None
    for task in tasks:
        if res is None:
            res = task
            continue

        if not _push_task(task):
            task.future.set_result(None)
    return res


def _cancel_all_tasks_if_no_available_translate_provider():
    if _has_available_translate_provider():
        return

    logger.warning('No available translate provider')
    for queue in _task_queues:
        while not queue.empty():
            task = queue.get_nowait()
            task.future.set_result(None)


def _has_available_translate_provider():
    return any(provider.is_available for provider in _translate_providers)


class TranslateProvider:
    def __init__(self, query_interval):
        self._query_interval = query_interval
        self._be_available_event = asyncio.Event()
        self._be_available_event.set()

    async def init(self):
        utils.async_io.create_task_with_ref(self._translate_consumer())
        return True

    @property
    def is_available(self):
        return True

    def _on_availability_change(self):
        if self.is_available:
            self._be_available_event.set()
        else:
            self._be_available_event.clear()
            _cancel_all_tasks_if_no_available_translate_provider()

    async def _translate_consumer(self):
        cls_name = type(self).__name__
        while True:
            try:
                if not self.is_available:
                    logger.info('%s waiting to become available', cls_name)
                    await self._be_available_event.wait()
                    logger.info('%s became available', cls_name)

                task = await _pop_task()
                # 为了简化代码，约定只会在_translate_wrapper里变成不可用，所以获取task之后这里还是可用的
                assert self.is_available

                start_time = datetime.datetime.now()
                await self._translate_wrapper(task)
                cost_time = (datetime.datetime.now() - start_time).total_seconds()

                # 频率限制
                await asyncio.sleep(self._query_interval - cost_time)
            except Exception:  # noqa
                logger.exception('%s error:', cls_name)

    async def _translate_wrapper(self, task: TranslateTask) -> Optional[str]:
        try:
            exc = None
            task.remain_retry_count -= 1
            res = await self._do_translate(task.text)
        except BaseException as e:
            exc = e
            res = None
        if res is not None:
            task.future.set_result(res)
            return res

        if task.remain_retry_count > 0:
            # 还可以重试则放回队列
            if not _push_task(task):
                task.future.set_result(None)
        else:
            # 否则设置异常或None结果
            if exc is not None:
                task.future.set_exception(exc)
            else:
                task.future.set_result(None)
        return None

    async def _do_translate(self, text) -> Optional[str]:
        raise NotImplementedError


class TencentTranslateFree(TranslateProvider):
    def __init__(self, query_interval, source_language, target_language):
        super().__init__(query_interval)
        self._be_available_event.clear()  # _do_init之后才可用
        self._source_language = source_language
        self._target_language = target_language

        self._server_time_delta = 0
        self._uc_key = self._uc_iv = ''
        self._qtv = self._qtk = ''
        self._reinit_future = None

        # 连续失败的次数
        self._fail_count = 0

    async def init(self):
        if not await super().init():
            return False
        self._reinit_future = asyncio.create_task(self._reinit_coroutine())
        return True

    async def _do_init(self):
        try:
            async with utils.request.http_session.get('https://fanyi.qq.com/') as r:
                if r.status != 200:
                    logger.warning('TencentTranslateFree init request failed: status=%d %s', r.status, r.reason)
                    return False
                html = await r.text()

                try:
                    server_time = r.headers['Date']
                    server_time = datetime.datetime.strptime(server_time, '%a, %d %b %Y %H:%M:%S GMT')
                    server_time = server_time.replace(tzinfo=datetime.timezone.utc).timestamp()
                    self._server_time_delta = int((datetime.datetime.now().timestamp() - server_time) * 1000)
                except (KeyError, ValueError):
                    self._server_time_delta = 0
        except (aiohttp.ClientError, asyncio.TimeoutError):
            logger.exception('TencentTranslateFree init error:')
            return False

        # 获取token URL
        m = re.search(r"""\breauthuri\s*=\s*['"](.+?)['"]""", html)
        if m is None:
            logger.exception('TencentTranslateFree init failed: reauthuri not found')
            return False
        reauthuri = m[1]

        # 获取验证用的key、iv
        m = re.search(r"""\s*=\s*['"]((?:\w+\|\w+-)+\w+\|\w+)['"]""", html)
        if m is None:
            logger.exception('TencentTranslateFree init failed: initial global variables not found')
            return False
        uc_key = None
        uc_iv = None
        for item in m[1].split('-'):
            key, _, value = item.partition('|')
            if key == 'a137':
                uc_key = value
            elif key == 'E74':
                uc_iv = value
            if uc_key is not None and uc_iv is not None:
                break

        # 获取token
        try:
            async with utils.request.http_session.post('https://fanyi.qq.com/api/' + reauthuri) as r:
                if r.status != 200:
                    logger.warning('TencentTranslateFree init request failed: reauthuri=%s, status=%d %s',
                                   reauthuri, r.status, r.reason)
                    return False
                data = await r.json()
        except (aiohttp.ClientError, asyncio.TimeoutError):
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

        self._uc_key = uc_key
        self._uc_iv = uc_iv
        self._qtv = qtv
        self._qtk = qtk

        self._on_availability_change()
        return True

    async def _reinit_coroutine(self):
        while True:
            logger.debug('TencentTranslateFree reinit')
            start_time = datetime.datetime.now()
            try:
                await self._do_init()
            except Exception:  # noqa
                pass
            cost_time = (datetime.datetime.now() - start_time).total_seconds()

            await asyncio.sleep(30 - cost_time)

    @property
    def is_available(self):
        return '' not in (self._uc_key, self._uc_iv, self._qtv, self._qtk) and super().is_available

    async def _translate_wrapper(self, task: TranslateTask) -> Optional[str]:
        res = await super()._translate_wrapper(task)
        if res is not None:
            self._fail_count = 0
        else:
            self._on_fail()
        return res

    async def _do_translate(self, text) -> Optional[str]:
        try:
            async with utils.request.http_session.post(
                'https://fanyi.qq.com/api/translate',
                headers={
                    'Referer': 'https://fanyi.qq.com/',
                    'uc': self._get_uc()
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
                self._update_uc_key(r)
                data = await r.json()
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None
        if data['errCode'] != 0:
            logger.warning('TencentTranslateFree failed: %d %s', data['errCode'], data['errMsg'])
            return None
        res = ''.join(record['targetText'] for record in data['translate']['records'])
        if res == '' and text.strip() != '':
            # qtv、qtk过期
            logger.info('TencentTranslateFree result is empty %s', data)
            return None
        return res

    def _get_uc(self):
        user_actions = self._gen_user_actions()
        cur_timestamp = str(int(datetime.datetime.now().timestamp() * 1000))
        server_time_delta = str(self._server_time_delta)
        uc = '|'.join([user_actions, cur_timestamp, server_time_delta])

        aes = cry_aes.new(self._uc_key.encode('utf-8'), cry_aes.MODE_CBC, self._uc_iv.encode('utf-8'))
        uc = cry_pad.pad(uc.encode('utf-8'), aes.block_size, 'pkcs7')
        uc = aes.encrypt(uc)
        uc = base64.b64encode(uc).decode('utf-8')
        return uc

    @staticmethod
    def _gen_user_actions():
        # 1：点击翻译；2：源输入框聚焦或失去焦点；3：点击源语言列表；4：点击交换语言；5：点击目标语言列表；6：源输入框输入、粘贴
        user_actions = []
        if random.randint(1, 5) == 1:
            for i in range(random.randint(1, 2)):
                user_actions.append('2')
        user_actions.append('6')
        for i in range(random.randint(0, 6)):
            user_actions.append(random.choice('26'))
        if random.randint(1, 5) == 1:
            user_actions.append('1')
        return ''.join(user_actions)

    def _update_uc_key(self, r):
        try:
            hf_f = r.headers['f']
            hf_ts = int(r.headers['ts'])
        except (KeyError, ValueError):
            return

        cur_timestamp = int(datetime.datetime.now().timestamp() * 1000)
        hf_f = base64.b64decode(hf_f.encode('utf-8')).decode('utf-8')
        pos = int(hf_f[72: 72 + 4])
        uc_key = hf_f[pos: pos + 16]
        uc_iv = hf_f[pos + 16: pos + 16 + 16]

        self._server_time_delta = cur_timestamp - hf_ts
        self._uc_key = uc_key
        self._uc_iv = uc_iv

    def _on_fail(self):
        self._fail_count += 1
        # 为了可靠性，连续失败5次时冷却直到下次重新init
        if self._fail_count >= 5:
            self._cool_down()

    def _cool_down(self):
        logger.info('TencentTranslateFree is cooling down')
        # 下次_do_init后恢复
        self._uc_key = self._uc_iv = ''
        self._qtv = self._qtk = ''
        self._fail_count = 0

        self._on_availability_change()


class TencentTranslate(TranslateProvider):
    def __init__(self, query_interval, source_language, target_language,
                 secret_id, secret_key, region):
        super().__init__(query_interval)
        self._source_language = source_language
        self._target_language = target_language
        self._secret_id = secret_id
        self._secret_key = secret_key
        self._region = region

        self._cool_down_timer_handle = None

    @property
    def is_available(self):
        return self._cool_down_timer_handle is None and super().is_available

    async def _do_translate(self, text) -> Optional[str]:
        try:
            async with self._request_tencent_cloud(
                'TextTranslate',
                '2018-03-21',
                {
                    'SourceText': text,
                    'Source': self._source_language,
                    'Target': self._target_language,
                    'ProjectId': 0
                }
            ) as r:
                if r.status != 200:
                    logger.warning('TencentTranslate request failed: status=%d %s', r.status, r.reason)
                    return None
                data = (await r.json())['Response']
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            return None
        error = data.get('Error', None)
        if error is not None:
            logger.warning('TencentTranslate failed: %s %s, RequestId=%s', error['Code'],
                           error['Message'], data['RequestId'])
            self._on_fail(error['Code'])
            return None
        return data['TargetText']

    def _request_tencent_cloud(self, action, version, body):
        body_bytes = json.dumps(body).encode('utf-8')

        canonical_headers = 'content-type:application/json; charset=utf-8\nhost:tmt.tencentcloudapi.com\n'
        signed_headers = 'content-type;host'
        hashed_request_payload = hashlib.sha256(body_bytes).hexdigest()
        canonical_request = f'POST\n/\n\n{canonical_headers}\n{signed_headers}\n{hashed_request_payload}'

        request_timestamp = int(datetime.datetime.now().timestamp())
        date = datetime.datetime.utcfromtimestamp(request_timestamp).strftime('%Y-%m-%d')
        credential_scope = f'{date}/tmt/tc3_request'
        hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        string_to_sign = f'TC3-HMAC-SHA256\n{request_timestamp}\n{credential_scope}\n{hashed_canonical_request}'

        def sign(key, msg):
            return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

        secret_date = sign(('TC3' + self._secret_key).encode('utf-8'), date)
        secret_service = sign(secret_date, 'tmt')
        secret_signing = sign(secret_service, 'tc3_request')
        signature = hmac.new(secret_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        authorization = (
            f'TC3-HMAC-SHA256 Credential={self._secret_id}/{credential_scope}, '
            f'SignedHeaders={signed_headers}, Signature={signature}'
        )

        headers = {
            'Authorization': authorization,
            'Content-Type': 'application/json; charset=utf-8',
            'X-TC-Action': action,
            'X-TC-Version': version,
            'X-TC-Timestamp': str(request_timestamp),
            'X-TC-Region': self._region
        }

        return utils.request.http_session.post('https://tmt.tencentcloudapi.com/', headers=headers, data=body_bytes)

    def _on_fail(self, code):
        if self._cool_down_timer_handle is not None:
            return

        sleep_time = 0
        if code == 'FailedOperation.NoFreeAmount':
            # 下个月恢复免费额度
            cur_time = datetime.datetime.now()
            year = cur_time.year
            month = cur_time.month + 1
            if month > 12:
                year += 1
                month = 1
            next_month_time = datetime.datetime(year, month, 1, minute=5)
            sleep_time = (next_month_time - cur_time).total_seconds()
            # Python 3.8之前不能超过一天
            sleep_time = min(sleep_time, 24 * 60 * 60 - 1)
        elif code in ('FailedOperation.ServiceIsolate', 'LimitExceeded'):
            # 需要手动处理，等5分钟
            sleep_time = 5 * 60
        if sleep_time != 0:
            self._cool_down_timer_handle = asyncio.get_running_loop().call_later(
                sleep_time, self._on_cool_down_timeout
            )
            self._on_availability_change()

    def _on_cool_down_timeout(self):
        self._cool_down_timer_handle = None
        self._on_availability_change()


class BaiduTranslate(TranslateProvider):
    def __init__(self, query_interval, source_language, target_language,
                 app_id, secret):
        super().__init__(query_interval)
        self._source_language = source_language
        self._target_language = target_language
        self._app_id = app_id
        self._secret = secret

        self._cool_down_timer_handle = None

    @property
    def is_available(self):
        return self._cool_down_timer_handle is None and super().is_available

    async def _do_translate(self, text) -> Optional[str]:
        try:
            async with utils.request.http_session.post(
                'https://fanyi-api.baidu.com/api/trans/vip/translate',
                data=self._add_sign({
                    'q': text,
                    'from': self._source_language,
                    'to': self._target_language,
                    'appid': self._app_id,
                    'salt': random.randint(1, 999999999)
                })
            ) as r:
                if r.status != 200:
                    logger.warning('BaiduTranslate request failed: status=%d %s', r.status, r.reason)
                    return None
                data = await r.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            return None
        error_code = data.get('error_code', None)
        if error_code is not None:
            logger.warning('BaiduTranslate failed: %s %s', error_code, data['error_msg'])
            self._on_fail(error_code)
            return None
        return ''.join(result['dst'] for result in data['trans_result'])

    def _add_sign(self, data):
        str_to_sign = f"{self._app_id}{data['q']}{data['salt']}{self._secret}"
        sign = hashlib.md5(str_to_sign.encode('utf-8')).hexdigest()
        return {**data, 'sign': sign}

    def _on_fail(self, code):
        if self._cool_down_timer_handle is not None:
            return

        sleep_time = 0
        if code == '54004':
            # 账户余额不足，需要手动处理，等5分钟
            sleep_time = 5 * 60
        if sleep_time != 0:
            self._cool_down_timer_handle = asyncio.get_running_loop().call_later(
                sleep_time, self._on_cool_down_timeout
            )
            self._on_availability_change()

    def _on_cool_down_timeout(self):
        self._cool_down_timer_handle = None
        self._on_availability_change()


class GeminiTranslate(TranslateProvider):
    def __init__(self, query_interval, proxy, api_key, model_code, prompt, temperature):
        super().__init__(query_interval)
        self._proxy = proxy or None
        self._api_key = api_key
        self._url = f'https://generativelanguage.googleapis.com/v1beta/{model_code}:generateContent'
        self._prompt = prompt
        self._body = {
            'contents': [
                {
                    # 'role': 'user',
                    'parts': [{'text': ''}]
                }
            ],
            'safetySettings': [
                {
                    'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
                    'threshold': 'BLOCK_NONE'
                },
                {
                    'category': 'HARM_CATEGORY_HATE_SPEECH',
                    'threshold': 'BLOCK_NONE'
                },
                {
                    'category': 'HARM_CATEGORY_HARASSMENT',
                    'threshold': 'BLOCK_NONE'
                },
                {
                    'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
                    'threshold': 'BLOCK_NONE'
                }
            ],
            'generationConfig': {
                'temperature': temperature,
                'topP': 1,
                'topK': 32,
                'candidateCount': 1,
                'maxOutputTokens': 8192
            }
        }

        self._cool_down_timer_handle = None

    @property
    def is_available(self):
        return self._cool_down_timer_handle is None and super().is_available

    async def _do_translate(self, text) -> Optional[str]:
        input_text = self._prompt.format(original_text=text)
        self._body['contents'][0]['parts'][0]['text'] = input_text
        try:
            async with utils.request.http_session.post(
                self._url,
                params={'key': self._api_key},
                json=self._body,
                proxy=self._proxy,
            ) as r:
                if r.status != 200:
                    logger.warning('GeminiTranslate request failed: status=%d %s', r.status, r.reason)
                    self._on_fail(r.status)
                    return None
                data = await r.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError) as e:
            logger.warning('GeminiTranslate request failed, %s: %s', type(e).__name__, e)
            return None

        try:
            candidates = data['candidates']
            if not candidates:
                block_reason = data['promptFeedback'].get('blockReason', '')
                logger.warning('GeminiTranslate no candidate, block_reason=%s, text=%s', block_reason, text)
                return None

            first_content_parts = candidates[0]['content']['parts']
            return ''.join(part.get('text', '') for part in first_content_parts)
        except (KeyError, IndexError):
            logger.warning('GeminiTranslate failed to parse response: %s', data)
            return None

    def _on_fail(self, code):
        if self._cool_down_timer_handle is not None:
            return

        if code in (401, 403):
            # API密钥无效，没有权限，或者不在有效地区。需要手动处理，等5分钟
            self._cool_down_timer_handle = asyncio.get_running_loop().call_later(
                5 * 60, self._on_cool_down_timeout
            )
            self._on_availability_change()

    def _on_cool_down_timeout(self):
        self._cool_down_timer_handle = None
        self._on_availability_change()
