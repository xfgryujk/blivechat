# -*- coding: utf-8 -*-
import asyncio
from typing import *

import aiohttp
import http.cookies

# 不带这堆头部有时候也能成功请求，但是带上后成功的概率更高
BILIBILI_COMMON_HEADERS = {
    'Origin': 'https://www.bilibili.com',
    'Referer': 'https://www.bilibili.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/114.0.0.0 Safari/537.36'
}

http_session: Optional[aiohttp.ClientSession] = None


def init(SESSDATA:str=''):
    global http_session
    http_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
    if(SESSDATA!=''):
        cookie = http.cookies.SimpleCookie()
        cookie['SESSDATA'] = SESSDATA
        http_session.cookie_jar.update_cookies(cookie)

async def shut_down():
    if http_session is not None:
        await http_session.close()
