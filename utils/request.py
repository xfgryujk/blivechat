# -*- coding: utf-8 -*-
import asyncio
from typing import *

import aiohttp

# 不带这堆头部有时候也能成功请求，但是带上后成功的概率更高
BILIBILI_COMMON_HEADERS = {
    'Origin': 'https://www.bilibili.com',
    'Referer': 'https://www.bilibili.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/114.0.0.0 Safari/537.36'
}

http_session: Optional[aiohttp.ClientSession] = None


def init():
    # ClientSession要在异步函数中创建
    async def do_init():
        global http_session
        http_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))

    asyncio.get_event_loop().run_until_complete(do_init())
