# -*- coding: utf-8 -*-
import os
import logging
import http.cookies

import aiohttp

import config

logger = logging.getLogger(__name__)

# 不带这堆头部有时候也能成功请求，但是带上后成功的概率更高
BILIBILI_COMMON_HEADERS = {
    'Origin': 'https://www.bilibili.com',
    'Referer': 'https://www.bilibili.com/',
    'Sec-CH-UA': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    'Sec-CH-UA-Mobile': '?0',
    'Sec-CH-UA-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/105.0.0.0 Safari/537.36'
}
BILIBILI_COMMON_COOKIES = {
    'b_lsid': '639B17D4_9876590D28',
    '_uuid': '883B5256-A359-E4A3-7159-123456794937E96237infoc'
}

config.init()
cfg = config.get_config()

def load_bilibili_cookies():
    cookies = http.cookies.SimpleCookie()
    if cfg.bilibili_cookies_file:
        cookies_fn = os.path.join(config.BASE_PATH, cfg.bilibili_cookies_file)
        try:
            with open(cookies_fn, 'rt') as f:
                cookies.load(f.read())
            for cookie in cookies.values():
                cookie['domain'] = cookie['domain'] or '.bilibili.com'
        except FileNotFoundError:
            logger.warning("Cookies file not found, check if config is correct")
        for key in ['SESSDATA', 'bili_jct']:
            if key not in cookies:
                logger.warning("Missing necessary cookie entries, please check cookie file content and format")
                break
    return cookies

cookie_jar = aiohttp.CookieJar()
cookie_jar.update_cookies(load_bilibili_cookies())
http_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10), cookie_jar=cookie_jar)
