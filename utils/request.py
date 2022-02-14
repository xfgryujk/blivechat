# -*- coding: utf-8 -*-
import aiohttp

http_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
