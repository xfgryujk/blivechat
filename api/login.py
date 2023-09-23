# -*- coding: utf-8 -*-
import asyncio
import enum
import json
import logging
import random
import time
import uuid
from typing import *

from datetime import datetime

import aiohttp
import tornado.websocket

import api.base 
import config
import services.avatar
import services.chat
import services.translate
import utils.request
from aiohttp import ClientSession, CookieJar

import shelve
import qrcode
from PIL import Image
import io
import base64

logger = logging.getLogger(__name__)

class StatusHandler(api.base.ApiHandler):  # noqa
    async def get(self):
        with shelve.open('data/login') as db:
            cookie = db.get('cookie')
            if cookie is None:
                self.write({
                    'is_login': False
                })
                return 
            self.write({
                'is_login': True,
                'login_date': db.get('date')
            })
        
        
class KillHandler(api.base.ApiHandler):  # noqa
    async def get(self):
        with shelve.open('data/login') as db:
            del db['cookie']
            del db['date'] 
        utils.request.reload_cookie()
        self.write({})    


class StartHandler(api.base.ApiHandler):  # noqa
    async def get(self):  
        async with ClientSession(cookies={'appkey': 'aae92bc66f3edfab'}) as session:
            res = await session.get('https://passport.bilibili.com/x/passport-login/web/qrcode/generate', params={'source': 'live_pc'})
            data = await res.json()
            login_url = data['data']['url']
            qrcode_key = data['data']['qrcode_key']
            
            img = qrcode.make(login_url)
            # Save the image to byte array
            byte_arr = io.BytesIO()
            img.save(byte_arr, format='PNG')
            byte_arr = byte_arr.getvalue() 
            
            b64 = base64.b64encode(byte_arr)
            
            self.write({
                'qr': b64.decode('utf-8'),
                'key': qrcode_key
            })


class CheckHandler(api.base.ApiHandler):  # noqa
    async def get(self):
        async with ClientSession(cookies={'appkey': 'aae92bc66f3edfab'}) as session:
            qrcode_key = self.get_query_argument('qrcode_key')  
            
            res = await session.get('https://passport.bilibili.com/x/passport-login/web/qrcode/poll', params={'qrcode_key': qrcode_key})
            data = await res.json()
            
            state = data['data']['code'] 
            if state == 0: 
                res = await session.get('https://data.bilibili.com/v/')
                cookies = session.cookie_jar.filter_cookies('https://bilibili.com')
                with shelve.open('data/login') as db:
                    db['cookie'] = cookies
                    db['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                utils.request.reload_cookie()
                self.write({
                    'ok': True,
                }) 
            else: 
                self.write({
                    'ok': False,
                })


ROOM_INIT_URL = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom'
DANMAKU_SERVER_CONF_URL = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo'
 

class AuthHandler(api.base.ApiHandler):  # noqa
    async def get(self):
        try:
            room_id = int(self.get_query_argument('room_id'))
            
            cookie = None
            with shelve.open('data/login') as db:
                cookie = db.get('cookie')
             
            async with ClientSession() as session:
                res = await session.get(ROOM_INIT_URL, params={'room_id': room_id})
                if res.status != 200:
                    logger.warning('room=%d getInfoByRoom() failed, status=%d, reason=%s', room_id,
                                   res.status, res.reason)
                    return
                data = await res.json()
                if data['code'] != 0:
                    logger.warning('room=%d getInfoByRoom() failed, message=%s', room_id,
                                   data['message'])
                    return
                            
                room_info = data['data']['room_info']
                room_id = room_info['room_id']
                room_short_id = room_info['short_id']
                room_owner_uid = room_info['uid']
                 
                if cookie is not None: 
                    session.cookie_jar.update_cookies(cookie)
                    
                res = await session.get(DANMAKU_SERVER_CONF_URL, params={'id': room_id, 'type': 0})
                if res.status != 200:
                    logger.warning('room=%d getDanmuInfo() failed, status=%d, reason=%s', room_id,
                                   res.status, res.reason)
                    return
                data = await res.json()
                if data['code'] != 0:
                    logger.warning('room=%d getDanmuInfo() failed, message=%s', room_id,
                                   data['message'])
                    return 
                
                data = data['data']
                token = data['token']
                
                if cookie is None: 
                    self.write({
                        'uid': 0,
                        'roomid': room_id,
                        'protover': 3,
                        'platform': 'web',
                        'key': token
                    })
                    return    
                else:
                    user_id = cookie['DedeUserID'].value
                    buvid = cookie['buvid3'].value
                    self.write({
                        'uid': int(user_id),
                        'roomid': room_id,
                        'protover': 3,
                        'platform': 'web',
                        'key': token,
                        'buvid': buvid,
                        'type': 2
                    })
                    return
                 
        except Exception as ex:
            logger.exception(ex)
 
ROUTES = [
    (r'/api/login/status', StatusHandler),
    (r'/api/login/start', StartHandler),
    (r'/api/login/check', CheckHandler),
    (r'/api/login/auth', AuthHandler),
    (r'/api/login/kill', KillHandler),
]
