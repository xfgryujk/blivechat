# -*- coding: utf-8 -*-
import asyncio
import dataclasses
import logging
import os
import pickle
import sys
from typing import *

import aiohttp
import yarl

import app
import config

logger = logging.getLogger('login.' + __name__)

_BILIBILI_DOMAIN = 'bilibili.com'
_USER_INFO_URL = 'https://api.bilibili.com/x/web-interface/nav'

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # 被PyInstaller打包了，用当前目录计算
    _BLC_COOKIE_JAR_PATH = os.path.realpath(os.path.join('..', '..', 'cookie_jar.pickle'))
else:
    _BLC_COOKIE_JAR_PATH = os.path.realpath(os.path.join(config.BASE_PATH, '..', '..', 'data', 'cookie_jar.pickle'))

_logic_loop: Optional[asyncio.AbstractEventLoop] = None
_http_session: Optional[aiohttp.ClientSession] = None

# 用来防重
_validating_sessdata_set: Set[str] = set()


def init():
    global _logic_loop, _http_session
    _logic_loop = asyncio.get_running_loop()
    _http_session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=10),
    )

    _logic_loop.create_task(_validate_on_startup())


async def shut_down():
    if _http_session is not None:
        await _http_session.close()


async def _validate_on_startup():
    """如果未登录则打开登录窗口"""
    # 等主线程初始化
    sleep_task = asyncio.create_task(asyncio.sleep(2))

    app_ = app.get_app()
    if app_.is_standalone_mode:
        await sleep_task
        app_.open_admin_ui()
        return

    cookie_jar = _load_blc_cookies()
    if cookie_jar is not None:
        user_info = await _get_user_info_from_cookies(cookie_jar)
        if user_info is not None:
            logger.info('Found logged in user: uid=%d, name=%s', user_info.uid, user_info.name)
            return

    logger.info('No user info. Please log in')
    await sleep_task
    app_.open_admin_ui()


def _load_blc_cookies():
    try:
        cookie_jar = aiohttp.CookieJar()
        cookie_jar.load(_BLC_COOKIE_JAR_PATH)
        return cookie_jar
    except (OSError, pickle.PickleError):
        return None


def _save_blc_cookies(cookie_jar: aiohttp.CookieJar):
    logger.info('Saving cookies')

    tmp_path = _BLC_COOKIE_JAR_PATH + '.tmp'
    cookie_jar.save(tmp_path)
    os.replace(tmp_path, _BLC_COOKIE_JAR_PATH)

    logger.info('Cookies saved. Please restart blivechat to take effect')


async def validate_and_save_cookies(cookie_jar: aiohttp.CookieJar):
    sessdata = _get_sessdata(cookie_jar)
    if sessdata is None or sessdata in _validating_sessdata_set:
        return False
    _validating_sessdata_set.add(sessdata)

    try:
        user_info = await _get_user_info_from_cookies(cookie_jar)
        if user_info is None:
            return False
        logger.info('Got user info: uid=%d, name=%s', user_info.uid, user_info.name)

        _save_blc_cookies(cookie_jar)
        return True
    except:
        _validating_sessdata_set.discard(sessdata)
        raise


def _get_sessdata(cookie_jar: aiohttp.CookieJar):
    cookies = cookie_jar.filter_cookies(yarl.URL(_USER_INFO_URL))
    sessdata_cookie = cookies.get('SESSDATA', None)
    if sessdata_cookie is None or sessdata_cookie.value == '':
        return None
    return sessdata_cookie.value


@dataclasses.dataclass
class BilibiliUserInfo:
    uid: int
    name: str


async def _get_user_info_from_cookies(cookie_jar: aiohttp.CookieJar):
    if _get_sessdata(cookie_jar) is None:
        logger.info('Failed to get user info: no SESSDATA')
        return None

    try:
        async with _http_session.get(
            _USER_INFO_URL,
            cookies=cookie_jar.filter_cookies(yarl.URL(_USER_INFO_URL)),
            headers={'User-Agent': config.USER_AGENT},
        ) as res:
            res.raise_for_status()

            data = await res.json()
            if data['code'] != 0:
                if data['code'] == -101:
                    logger.info('Failed to get user info: not logged in')
                else:
                    logger.warning('Failed to get user info: code=%d, message=%s', data['code'], data['message'])
                return None

            data = data['data']
            if not data['isLogin']:
                logger.info('Failed to get user info: not logged in')
                return None

            return BilibiliUserInfo(
                uid=data['mid'],
                name=data['uname'],
            )
    except aiohttp.ClientError as e:
        logger.warning('Failed to get user info: %s', e)
        return None
