# -*- coding: utf-8 -*-
import asyncio
import dataclasses
import datetime
import hashlib
import logging
import re
import urllib.parse
from typing import *

import aiohttp
import cachetools
import sqlalchemy.exc

import config
import models.bilibili as bl_models
import models.database
import utils.request

logger = logging.getLogger(__name__)


DEFAULT_AVATAR_URL = '//static.hdslb.com/images/member/noface.gif'

_avatar_fetchers: List['AvatarFetcher'] = []
# user_id -> avatar_url
_avatar_url_cache: Optional[cachetools.TTLCache] = None
# 正在获取头像的Future，user_id -> Future
_uid_fetch_future_map: Dict[int, asyncio.Future] = {}
# 正在获取头像的任务队列
_task_queue: Optional['asyncio.Queue[FetchTask]'] = None


@dataclasses.dataclass
class FetchTask:
    user_id: int
    future: 'asyncio.Future[Optional[str]]'


def init():
    cfg = config.get_config()
    global _avatar_url_cache, _task_queue
    _avatar_url_cache = cachetools.TTLCache(cfg.avatar_cache_size, 10 * 60)
    _task_queue = asyncio.Queue(cfg.fetch_avatar_max_queue_size)
    asyncio.get_event_loop().create_task(_do_init())


async def _do_init():
    fetchers = [
        UserSpaceAvatarFetcher(5.5),
        MedalAnchorAvatarFetcher(3),
        UserCardAvatarFetcher(3),
        GameUserCenterAvatarFetcher(3),
    ]
    await asyncio.gather(*(fetcher.init() for fetcher in fetchers))
    global _avatar_fetchers
    _avatar_fetchers = fetchers


async def get_avatar_url(user_id) -> str:
    avatar_url = await get_avatar_url_or_none(user_id)
    if avatar_url is None:
        avatar_url = DEFAULT_AVATAR_URL
    return avatar_url


async def get_avatar_url_or_none(user_id) -> Optional[str]:
    if user_id == 0:
        return None

    # 查内存
    avatar_url = _get_avatar_url_from_memory(user_id)
    if avatar_url is not None:
        return avatar_url

    # 查数据库
    user = await _get_avatar_url_from_database(user_id)
    if user is not None:
        avatar_url = user.avatar_url
        _update_avatar_cache_in_memory(user_id, avatar_url)
        # 如果距离数据库上次更新太久，则在后台从接口获取，并更新所有缓存
        if (datetime.datetime.now() - user.update_time).days >= 1:
            asyncio.create_task(_refresh_avatar_cache_from_web(user_id))
        return avatar_url

    # 从接口获取
    avatar_url = await _get_avatar_url_from_web(user_id)
    if avatar_url is not None:
        update_avatar_cache(user_id, avatar_url)
        return avatar_url

    return None


async def _refresh_avatar_cache_from_web(user_id):
    avatar_url = await _get_avatar_url_from_web(user_id)
    if avatar_url is None:
        return
    update_avatar_cache(user_id, avatar_url)


def update_avatar_cache(user_id, avatar_url):
    if user_id == 0:
        return
    _update_avatar_cache_in_memory(user_id, avatar_url)
    _update_avatar_cache_in_database(user_id, avatar_url)


def update_avatar_cache_if_expired(user_id, avatar_url):
    # 内存缓存过期了才更新，减少写入数据库的频率
    if _get_avatar_url_from_memory(user_id) is None:
        update_avatar_cache(user_id, avatar_url)


def process_avatar_url(avatar_url):
    # 去掉协议，兼容HTTP、HTTPS
    m = re.fullmatch(r'(?:https?:)?(.*)', avatar_url)
    if m is not None:
        avatar_url = m[1]
    # 缩小图片加快传输
    if not avatar_url.endswith('noface.gif'):
        avatar_url += '@48w_48h'
    return avatar_url


def _get_avatar_url_from_memory(user_id) -> Optional[str]:
    return _avatar_url_cache.get(user_id, None)


def _update_avatar_cache_in_memory(user_id, avatar_url):
    _avatar_url_cache[user_id] = avatar_url


def _get_avatar_url_from_database(user_id) -> Awaitable[Optional[bl_models.BilibiliUser]]:
    loop = asyncio.get_running_loop()
    return loop.run_in_executor(None, _do_get_avatar_url_from_database, user_id)


def _do_get_avatar_url_from_database(user_id) -> Optional[bl_models.BilibiliUser]:
    try:
        with models.database.get_session() as session:
            user: bl_models.BilibiliUser = session.scalars(
                sqlalchemy.select(bl_models.BilibiliUser).filter(
                    bl_models.BilibiliUser.uid == user_id
                )
            ).one_or_none()
            if user is None:
                return None
            return user
    except sqlalchemy.exc.OperationalError:
        # SQLite会锁整个文件，忽略就行
        return None
    except sqlalchemy.exc.SQLAlchemyError:
        logger.exception('_do_get_avatar_url_from_database failed:')
        return None


def _update_avatar_cache_in_database(user_id, avatar_url) -> Awaitable[None]:
    return asyncio.get_running_loop().run_in_executor(
        None, _do_update_avatar_cache_in_database, user_id, avatar_url
    )


def _do_update_avatar_cache_in_database(user_id, avatar_url):
    try:
        with models.database.get_session() as session:
            user = session.scalars(
                sqlalchemy.select(bl_models.BilibiliUser).filter(
                    bl_models.BilibiliUser.uid == user_id
                )
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
        # SQLite会锁整个文件，忽略就行。另外还有多线程导致ID重复的问题，这里对一致性要求不高就没加for update
        pass
    except sqlalchemy.exc.SQLAlchemyError:
        logger.exception('_do_update_avatar_cache_in_database failed:')


def _get_avatar_url_from_web(user_id) -> Awaitable[Optional[str]]:
    # 如果已有正在获取的future则返回，防止重复获取同一个uid
    future = _uid_fetch_future_map.get(user_id, None)
    if future is not None:
        return future
    # 否则创建一个获取任务
    future = asyncio.get_running_loop().create_future()

    task = FetchTask(
        user_id=user_id,
        future=future
    )
    if not _push_task(task):
        future.set_result(None)
        return future

    _uid_fetch_future_map[user_id] = future
    future.add_done_callback(lambda _future: _uid_fetch_future_map.pop(user_id, None))
    return future


def _push_task(task: FetchTask):
    if not _has_available_avatar_fetcher():
        return False

    try:
        _task_queue.put_nowait(task)
        return True
    except asyncio.QueueFull:
        return False


def _pop_task() -> Awaitable[FetchTask]:
    return _task_queue.get()


def _cancel_all_tasks_if_no_available_avatar_fetcher():
    if _has_available_avatar_fetcher():
        return

    logger.warning('No available avatar fetcher')
    while not _task_queue.empty():
        task = _task_queue.get_nowait()
        task.future.set_result(None)


def _has_available_avatar_fetcher():
    return any(fetcher.is_available for fetcher in _avatar_fetchers)


class AvatarFetcher:
    def __init__(self, query_interval):
        self._query_interval = query_interval
        self._be_available_event = asyncio.Event()
        self._be_available_event.set()

        self._cool_down_timer_handle = None

    async def init(self):
        asyncio.create_task(self._fetch_consumer())
        return True

    @property
    def is_available(self):
        return self._cool_down_timer_handle is None

    def _on_availability_change(self):
        if self.is_available:
            self._be_available_event.set()
        else:
            self._be_available_event.clear()
            _cancel_all_tasks_if_no_available_avatar_fetcher()

    async def _fetch_consumer(self):
        cls_name = type(self).__name__
        while True:
            try:
                if not self.is_available:
                    logger.info('%s waiting to become available', cls_name)
                    await self._be_available_event.wait()
                    logger.info('%s became available', cls_name)

                task = await _pop_task()
                # 为了简化代码，约定只会在_fetch_wrapper里变成不可用，所以获取task之后这里还是可用的
                assert self.is_available

                start_time = datetime.datetime.now()
                await self._fetch_wrapper(task)
                cost_time = (datetime.datetime.now() - start_time).total_seconds()

                # 限制频率，防止被B站ban
                await asyncio.sleep(self._query_interval - cost_time)
            except Exception:  # noqa
                logger.exception('%s error:', cls_name)

    async def _fetch_wrapper(self, task: FetchTask) -> Optional[str]:
        try:
            avatar_url = await self._do_fetch(task.user_id)
        except BaseException as e:
            task.future.set_exception(e)
            return None

        task.future.set_result(avatar_url)
        return avatar_url

    async def _do_fetch(self, user_id) -> Optional[str]:
        raise NotImplementedError

    def _cool_down(self, sleep_time):
        if self._cool_down_timer_handle is not None:
            return

        self._cool_down_timer_handle = asyncio.get_running_loop().call_later(
            sleep_time, self._on_cool_down_timeout
        )
        self._on_availability_change()

    def _on_cool_down_timeout(self):
        self._cool_down_timer_handle = None
        self._on_availability_change()


class UserSpaceAvatarFetcher(AvatarFetcher):
    # wbi密码表
    WBI_KEY_INDEX_TABLE = [
        46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
        27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13
    ]

    def __init__(self, query_interval):
        super().__init__(query_interval)

        # wbi鉴权口令
        self._wbi_key = ''

    async def _do_fetch(self, user_id) -> Optional[str]:
        if self._wbi_key == '':
            await self._refresh_wbi_key()
            if self._wbi_key == '':
                return None

        try:
            async with utils.request.http_session.get(
                'https://api.bilibili.com/x/space/wbi/acc/info',
                headers={
                    **utils.request.BILIBILI_COMMON_HEADERS,
                    'Origin': 'https://space.bilibili.com',
                    'Referer': f'https://space.bilibili.com/{user_id}/'
                },
                params=self._add_wbi_sign({'mid': user_id}),
            ) as r:
                if r.status != 200:
                    logger.warning(
                        'UserSpaceAvatarFetcher failed to fetch avatar: status=%d %s uid=%d',
                        r.status, r.reason, user_id
                    )
                    if r.status == 412:
                        # 被B站ban了
                        self._cool_down(3 * 60)
                        await self._refresh_wbi_key()
                    return None
                data = await r.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            return None

        code = data['code']
        if code != 0:
            logger.info(
                'UserSpaceAvatarFetcher failed to fetch avatar: code=%d %s uid=%d',
                code, data['message'], user_id
            )
            if code == -401:
                # 被B站ban了
                self._cool_down(3 * 60)
                await self._refresh_wbi_key()
            elif code == -403:
                # 签名错误
                self._wbi_key = ''
                await self._refresh_wbi_key()
            return None

        return process_avatar_url(data['data']['face'])

    async def _refresh_wbi_key(self):
        wbi_key = await self._get_wbi_key()
        if wbi_key != '':
            self._wbi_key = wbi_key

    async def _get_wbi_key(self):
        try:
            async with utils.request.http_session.get(
                'https://api.bilibili.com/nav',
                headers=utils.request.BILIBILI_COMMON_HEADERS,
            ) as r:
                if r.status != 200:
                    logger.warning('UserSpaceAvatarFetcher failed to get wbi key: status=%d %s', r.status, r.reason)
                    return ''
                data = await r.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            logger.exception('UserSpaceAvatarFetcher failed to get wbi key:')
            return ''

        try:
            wbi_img = data['data']['wbi_img']
            img_key = wbi_img['img_url'].rpartition('/')[2].partition('.')[0]
            sub_key = wbi_img['sub_url'].rpartition('/')[2].partition('.')[0]
        except KeyError:
            logger.warning('UserSpaceAvatarFetcher failed to get wbi key: data=%s', data)
            return ''

        shuffled_key = img_key + sub_key
        wbi_key = []
        for index in self.WBI_KEY_INDEX_TABLE:
            if index < len(shuffled_key):
                wbi_key.append(shuffled_key[index])
        return ''.join(wbi_key)

    def _add_wbi_sign(self, params: dict):
        if self._wbi_key == '':
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

        str_to_sign = urllib.parse.urlencode(params_to_sign) + self._wbi_key
        w_rid = hashlib.md5(str_to_sign.encode('utf-8')).hexdigest()
        return {
            **params,
            'wts': wts,
            'w_rid': w_rid
        }


class MedalAnchorAvatarFetcher(AvatarFetcher):
    async def _do_fetch(self, user_id) -> Optional[str]:
        try:
            async with utils.request.http_session.get(
                'https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuMedalAnchorInfo',
                headers={
                    **utils.request.BILIBILI_COMMON_HEADERS,
                    'Origin': 'https://live.bilibili.com',
                    'Referer': 'https://live.bilibili.com/'
                },
                params={
                    'ruid': user_id,
                    'token': '',
                    'platform': 'web',
                    'jsonp': 'jsonp'
                }
            ) as r:
                if r.status != 200:
                    logger.warning(
                        'MedalAnchorAvatarFetcher failed to fetch avatar: status=%d %s uid=%d',
                        r.status, r.reason, user_id
                    )
                    if r.status == 412:
                        # 被B站ban了
                        self._cool_down(3 * 60)
                    return None
                data = await r.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            return None

        code = data['code']
        if code != 0:
            # 这里虽然失败但不会被ban一段时间
            logger.info(
                'MedalAnchorAvatarFetcher failed to fetch avatar: code=%d %s uid=%d',
                code, data['message'], user_id
            )
            return None

        return process_avatar_url(data['data']['rface'])


class UserCardAvatarFetcher(AvatarFetcher):
    async def _do_fetch(self, user_id) -> Optional[str]:
        try:
            async with utils.request.http_session.get(
                'https://api.bilibili.com/x/web-interface/card',
                headers={
                    **utils.request.BILIBILI_COMMON_HEADERS,
                    'Origin': 'https://t.bilibili.com',
                    'Referer': 'https://t.bilibili.com/'
                },
                params={
                    'mid': user_id,
                    'photo': 'true'
                }
            ) as r:
                if r.status != 200:
                    logger.warning(
                        'UserCardAvatarFetcher failed to fetch avatar: status=%d %s uid=%d',
                        r.status, r.reason, user_id
                    )
                    if r.status == 412:
                        # 被B站ban了
                        self._cool_down(3 * 60)
                    return None
                data = await r.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            return None

        code = data['code']
        if code != 0:
            # 这里虽然失败但不会被ban一段时间
            logger.info(
                'UserCardAvatarFetcher failed to fetch avatar: code=%d %s uid=%d',
                code, data['message'], user_id
            )
            return None

        return process_avatar_url(data['data']['card']['face'])


class GameUserCenterAvatarFetcher(AvatarFetcher):
    async def _do_fetch(self, user_id) -> Optional[str]:
        try:
            async with utils.request.http_session.get(
                'https://line3-h5-mobile-api.biligame.com/game/center/h5/user/space/info',
                headers={
                    **utils.request.BILIBILI_COMMON_HEADERS,
                    'Origin': 'https://app.biligame.com',
                    'Referer': 'https://app.biligame.com/'
                },
                params={
                    'uid': user_id,
                    'sdk_type': '1'
                }
            ) as r:
                if r.status != 200:
                    # 这个接口经常502
                    logger.info(
                        'GameUserCenterAvatarFetcher failed to fetch avatar: status=%d %s uid=%d',
                        r.status, r.reason, user_id
                    )
                    if r.status == 412:
                        # 被B站ban了
                        self._cool_down(3 * 60)
                    return None
                data = await r.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            return None

        code = data['code']
        if code != 0:
            # 这里虽然失败但不会被ban一段时间
            logger.info(
                'GameUserCenterAvatarFetcher failed to fetch avatar: code=%d %s uid=%d',
                code, data['message'], user_id
            )
            return None

        return process_avatar_url(data['data']['face'])
