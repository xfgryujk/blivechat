# -*- coding: utf-8 -*-
import asyncio

import aiohttp

import utils.async_io
import utils.request

VERSION = 'v1.9.0'


def check_update():
    utils.async_io.create_task_with_ref(_do_check_update())


async def _do_check_update():
    try:
        async with utils.request.http_session.get(
            'https://api.github.com/repos/xfgryujk/blivechat/releases/latest'
        ) as r:
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
