# -*- coding: utf-8 -*-
import asyncio
import datetime
import hashlib
import logging
import re
import urllib.parse
from typing import *

import aiohttp
import sqlalchemy
import sqlalchemy.exc

import config
import models.bilibili as bl_models
import models.database
import utils.request

logger = logging.getLogger(__name__)


DEFAULT_AVATAR_URL = '//static.hdslb.com/images/member/noface.gif'

_main_event_loop = asyncio.get_event_loop()
# user_id -> avatar_url
_avatar_url_cache: Dict[int, str] = {}
# 正在获取头像的Future，user_id -> Future
_uid_fetch_future_map: Dict[int, asyncio.Future] = {}
# 正在获取头像的user_id队列
_uid_queue_to_fetch: Optional[asyncio.Queue] = None
# 上次被B站ban时间
_last_fetch_banned_time: Optional[datetime.datetime] = None

# wbi密码表
WBI_KEY_INDEX_TABLE = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
    27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13
]
# wbi鉴权口令
_wbi_key = ''


def init():
    cfg = config.get_config()
    global _uid_queue_to_fetch
    _uid_queue_to_fetch = asyncio.Queue(cfg.fetch_avatar_max_queue_size)
    asyncio.ensure_future(_get_avatar_url_from_web_consumer())


async def get_avatar_url(user_id):
    avatar_url = await get_avatar_url_or_none(user_id)
    if avatar_url is None:
        avatar_url = DEFAULT_AVATAR_URL
    return avatar_url


async def get_avatar_url_or_none(user_id):
    avatar_url = get_avatar_url_from_memory(user_id)
    if avatar_url is not None:
        return avatar_url
    avatar_url = await get_avatar_url_from_database(user_id)
    if avatar_url is not None:
        return avatar_url
    return await get_avatar_url_from_web(user_id)


def get_avatar_url_from_memory(user_id):
    return _avatar_url_cache.get(user_id, None)


def get_avatar_url_from_database(user_id) -> Awaitable[Optional[str]]:
    return asyncio.get_event_loop().run_in_executor(
        None, _do_get_avatar_url_from_database, user_id
    )


def _do_get_avatar_url_from_database(user_id):
    try:
        with models.database.get_session() as session:
            user = session.query(bl_models.BilibiliUser).filter(
                bl_models.BilibiliUser.uid == user_id
            ).one_or_none()
            if user is None:
                return None
            avatar_url = user.avatar_url

            # 如果离上次更新太久就更新所有缓存
            if (datetime.datetime.now() - user.update_time).days >= 3:
                def refresh_cache():
                    _avatar_url_cache.pop(user_id, None)
                    get_avatar_url_from_web(user_id)

                _main_event_loop.call_soon(refresh_cache)
            else:
                # 否则只更新内存缓存
                _update_avatar_cache_in_memory(user_id, avatar_url)
    except sqlalchemy.exc.OperationalError:
        # SQLite会锁整个文件，忽略就行
        return None
    except sqlalchemy.exc.SQLAlchemyError:
        logger.exception('_do_get_avatar_url_from_database failed:')
        return None
    return avatar_url


def get_avatar_url_from_web(user_id) -> Awaitable[Optional[str]]:
    # 如果已有正在获取的future则返回，防止重复获取同一个uid
    future = _uid_fetch_future_map.get(user_id, None)
    if future is not None:
        return future
    # 否则创建一个获取任务
    _uid_fetch_future_map[user_id] = future = _main_event_loop.create_future()
    future.add_done_callback(lambda _future: _uid_fetch_future_map.pop(user_id, None))
    try:
        _uid_queue_to_fetch.put_nowait(user_id)
    except asyncio.QueueFull:
        future.set_result(None)
    return future


async def _get_avatar_url_from_web_consumer():
    while True:
        try:
            user_id = await _uid_queue_to_fetch.get()
            future = _uid_fetch_future_map.get(user_id, None)
            if future is None:
                continue

            # 防止在被ban的时候获取
            global _last_fetch_banned_time
            if _last_fetch_banned_time is not None:
                cur_time = datetime.datetime.now()
                if (cur_time - _last_fetch_banned_time).total_seconds() < 3 * 60 + 3:
                    # 3分钟以内被ban，解封大约要15分钟
                    future.set_result(None)
                    continue
                else:
                    _last_fetch_banned_time = None

            asyncio.ensure_future(_get_avatar_url_from_web_coroutine(user_id, future))

            # 限制频率，防止被B站ban
            cfg = config.get_config()
            await asyncio.sleep(cfg.fetch_avatar_interval)
        except Exception:  # noqa
            logger.exception('_get_avatar_url_from_web_consumer error:')


async def _get_avatar_url_from_web_coroutine(user_id, future):
    try:
        avatar_url = await _do_get_avatar_url_from_web(user_id)
    except BaseException as e:
        future.set_exception(e)
    else:
        future.set_result(avatar_url)


async def _do_get_avatar_url_from_web(user_id):
    global _wbi_key
    if _wbi_key == '':
        # TODO 判断一下是否正在获取
        _wbi_key = await _get_wbi_key()

    try:
        async with utils.request.http_session.get(
            'https://api.bilibili.com/x/space/wbi/acc/info',
            headers={
                **utils.request.BILIBILI_COMMON_HEADERS,
                'Origin': 'https://space.bilibili.com',
                'Referer': f'https://space.bilibili.com/{user_id}/'
            },
            cookies=utils.request.BILIBILI_COMMON_COOKIES,
            params=_add_wbi_sign({'mid': user_id}),
        ) as r:
            if r.status != 200:
                logger.warning('Failed to fetch avatar: status=%d %s uid=%d', r.status, r.reason, user_id)
                if r.status == 412:
                    # 被B站ban了
                    global _last_fetch_banned_time
                    _last_fetch_banned_time = datetime.datetime.now()
                return None
            data = await r.json()
    except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
        return None

    if data['code'] != 0:
        # 这里虽然失败但不会被ban一段时间
        logger.info('Failed to fetch avatar: code=%d %s uid=%d', data['code'], data['message'], user_id)
        if data['code'] == -403:
            _wbi_key = ''
        return None

    avatar_url = process_avatar_url(data['data']['face'])
    update_avatar_cache(user_id, avatar_url)
    return avatar_url


async def _get_wbi_key():
    try:
        async with utils.request.http_session.get(
            'https://api.bilibili.com/nav',
            headers=utils.request.BILIBILI_COMMON_HEADERS,
        ) as r:
            if r.status != 200:
                logger.warning('Failed to get wbi key: status=%d %s', r.status, r.reason)
                return ''
            data = await r.json()
    except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
        logger.exception('Failed to get wbi key:')
        return ''

    try:
        wbi_img = data['data']['wbi_img']
        img_key = wbi_img['img_url'].rpartition('/')[2].partition('.')[0]
        sub_key = wbi_img['sub_url'].rpartition('/')[2].partition('.')[0]
    except KeyError:
        logger.warning('Failed to get wbi key: data=%s', data)
        return ''

    shuffled_key = img_key + sub_key
    wbi_key = []
    for index in WBI_KEY_INDEX_TABLE:
        if index < len(shuffled_key):
            wbi_key.append(shuffled_key[index])
    return ''.join(wbi_key)


def _add_wbi_sign(params: dict):
    if _wbi_key == '':
        return params

    wts = str(int(datetime.datetime.now().timestamp()))
    params_to_sign = {**params, 'wts': wts}

    # 按key字典序排序
    params_to_sign = {
        key: params_to_sign[key]
        for key in sorted(params_to_sign.keys())
    }
    # 过滤一些字符
    for key, value in params_to_sign.items():
        value = ''.join(
            ch
            for ch in str(value)
            if ch not in "!'()*"
        )
        params_to_sign[key] = value

    str_to_sign = urllib.parse.urlencode(params_to_sign) + _wbi_key
    w_rid = hashlib.md5(str_to_sign.encode('utf-8')).hexdigest()
    return {
        **params,
        'wts': wts,
        'w_rid': w_rid
    }


def process_avatar_url(avatar_url):
    # 去掉协议，兼容HTTP、HTTPS
    m = re.fullmatch(r'(?:https?:)?(.*)', avatar_url)
    if m is not None:
        avatar_url = m[1]
    # 缩小图片加快传输
    if not avatar_url.endswith('noface.gif'):
        avatar_url += '@48w_48h'
    return avatar_url


def update_avatar_cache(user_id, avatar_url):
    _update_avatar_cache_in_memory(user_id, avatar_url)
    asyncio.get_event_loop().run_in_executor(
        None, _update_avatar_cache_in_database, user_id, avatar_url
    )


def _update_avatar_cache_in_memory(user_id, avatar_url):
    _avatar_url_cache[user_id] = avatar_url
    cfg = config.get_config()
    while len(_avatar_url_cache) > cfg.avatar_cache_size:
        _avatar_url_cache.pop(next(iter(_avatar_url_cache)), None)


def _update_avatar_cache_in_database(user_id, avatar_url):
    try:
        with models.database.get_session() as session:
            user = session.query(bl_models.BilibiliUser).filter(
                bl_models.BilibiliUser.uid == user_id
            ).one_or_none()
            if user is None:
                user = bl_models.BilibiliUser(
                    uid=user_id
                )
                session.add(user)
            user.avatar_url = avatar_url
            user.update_time = datetime.datetime.now()
            session.commit()
    except (sqlalchemy.exc.OperationalError, sqlalchemy.exc.IntegrityError):
        # SQLite会锁整个文件，忽略就行，另外还有多线程导致ID重复的问题
        pass
    except sqlalchemy.exc.SQLAlchemyError:
        logger.exception('_update_avatar_cache_in_database failed:')
