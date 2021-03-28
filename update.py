# -*- coding: utf-8 -*-

import asyncio

import aiohttp

VERSION = 'v1.5.1'


def check_update():
    asyncio.ensure_future(_do_check_update())


async def _do_check_update():
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get('https://api.github.com/repos/xfgryujk/blivechat/releases/latest') as r:
                data = await r.json()
                if data['name'] != VERSION:
                    print('---------------------------------------------')
                    print('New version available:', data['name'])
                    print(data['body'])
                    print('Download:', data['html_url'])
                    print('---------------------------------------------')
    except aiohttp.ClientConnectionError:
        print('Failed to check update: connection failed')
    except asyncio.TimeoutError:
        print('Failed to check update: timeout')
