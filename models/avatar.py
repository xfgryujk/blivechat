# -*- coding: utf-8 -*-

import asyncio
import datetime
import logging
from typing import *

import aiohttp
import sqlalchemy
import sqlalchemy.exc

import models.database

logger = logging.getLogger(__name__)


DEFAULT_AVATAR_URL = '//static.hdslb.com/images/member/noface.gif'

_main_event_loop = asyncio.get_event_loop()
_http_session = aiohttp.ClientSession()
# user_id -> avatar_url
_avatar_url_cache: Dict[int, str] = {}
# (user_id, future)
_fetch_task_queue = asyncio.Queue(15)
_last_fetch_failed_time: Optional[datetime.datetime] = None


def init():
    asyncio.ensure_future(_get_avatar_url_from_web_consumer())


async def get_avatar_url(user_id):
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
            user = session.query(BilibiliUser).filter(BilibiliUser.uid == user_id).one_or_none()
            if user is None:
                return None
            avatar_url = user.avatar_url

            # 如果离上次更新太久就更新所有缓存
            if (datetime.datetime.now() - user.update_time).days >= 3:
                def refresh_cache():
                    try:
                        del _avatar_url_cache[user_id]
                    except KeyError:
                        pass
                    get_avatar_url_from_web(user_id)

                _main_event_loop.call_soon(refresh_cache)
            else:
                # 否则只更新内存缓存
                _update_avatar_cache_in_memory(user_id, avatar_url)
    except sqlalchemy.exc.SQLAlchemyError:
        return None
    return avatar_url


def get_avatar_url_from_web(user_id) -> Awaitable[str]:
    future = _main_event_loop.create_future()
    try:
        _fetch_task_queue.put_nowait((user_id, future))
    except asyncio.QueueFull:
        future.set_result(DEFAULT_AVATAR_URL)
    return future


async def _get_avatar_url_from_web_consumer():
    while True:
        try:
            user_id, future = await _fetch_task_queue.get()

            # 先查缓存，防止队列中出现相同uid时重复获取
            avatar_url = get_avatar_url_from_memory(user_id)
            if avatar_url is not None:
                continue

            # 防止在被ban的时候获取
            global _last_fetch_failed_time
            if _last_fetch_failed_time is not None:
                cur_time = datetime.datetime.now()
                if (cur_time - _last_fetch_failed_time).total_seconds() < 3 * 60 + 3:
                    # 3分钟以内被ban则先返回默认头像，解封大约要15分钟
                    return DEFAULT_AVATAR_URL
                else:
                    _last_fetch_failed_time = None

            asyncio.ensure_future(_get_avatar_url_from_web_coroutine(user_id, future))

            # 限制频率，防止被B站ban
            await asyncio.sleep(0.2)
        except:
            pass


async def _get_avatar_url_from_web_coroutine(user_id, future):
    try:
        avatar_url = await _do_get_avatar_url_from_web(user_id)
    except BaseException as e:
        future.set_exception(e)
        return
    future.set_result(avatar_url)


async def _do_get_avatar_url_from_web(user_id):
    try:
        async with _http_session.get('https://api.bilibili.com/x/space/acc/info',
                                     params={'mid': user_id}) as r:
            if r.status != 200:
                # 可能被B站ban了
                logger.warning('Failed to fetch avatar: status=%d %s uid=%d', r.status, r.reason, user_id)
                global _last_fetch_failed_time
                _last_fetch_failed_time = datetime.datetime.now()
                return DEFAULT_AVATAR_URL
            data = await r.json()
    except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
        return DEFAULT_AVATAR_URL

    avatar_url = data['data']['face'].replace('http:', '').replace('https:', '')
    if not avatar_url.endswith('noface.gif'):
        avatar_url += '@48w_48h'

    update_avatar_cache(user_id, avatar_url)
    return avatar_url


def update_avatar_cache(user_id, avatar_url):
    _update_avatar_cache_in_memory(user_id, avatar_url)
    asyncio.get_event_loop().run_in_executor(
        None, _update_avatar_cache_in_database, user_id, avatar_url
    )


def _update_avatar_cache_in_memory(user_id, avatar_url):
    _avatar_url_cache[user_id] = avatar_url
    if len(_avatar_url_cache) > 50000:
        for _, key in zip(range(100), _avatar_url_cache):
            del _avatar_url_cache[key]


def _update_avatar_cache_in_database(user_id, avatar_url):
    try:
        with models.database.get_session() as session:
            user = session.query(BilibiliUser).filter(BilibiliUser.uid == user_id).one_or_none()
            if user is None:
                user = BilibiliUser(uid=user_id, avatar_url=avatar_url,
                                    update_time=datetime.datetime.now())
                session.add(user)
            else:
                user.avatar_url = avatar_url
                user.update_time = datetime.datetime.now()
            session.commit()
    except sqlalchemy.exc.SQLAlchemyError:
        # SQLite会锁整个文件，忽略就行
        logger.exception('_update_avatar_cache_in_database failed:')


class BilibiliUser(models.database.OrmBase):
    __tablename__ = 'bilibili_users'
    uid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    avatar_url = sqlalchemy.Column(sqlalchemy.Text)
    update_time = sqlalchemy.Column(sqlalchemy.DateTime)
