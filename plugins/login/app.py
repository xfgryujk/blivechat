# -*- coding: utf-8 -*-
import asyncio
import concurrent.futures
import http.cookies
import logging
import threading
import time
from typing import *

import aiohttp
import webview

import blcsdk
import config
import cookies_mgr
import listener

logger = logging.getLogger('login.' + __name__)

_app: Optional['App'] = None


def init():
    global _app
    _app = App()
    _app.init()


def get_app():
    return _app


class App:
    def __init__(self):
        self._is_standalone_mode = False

        self._logic_worker = LogicWorker()

        self._browser_window = webview.create_window(
            title='登录B站账号',
            width=1100,
            height=700,
            hidden=True,
        )
        self._browser_window.events.closing += self._on_browser_closing
        self._browser_window.events.loaded += self._on_browser_loaded

    def init(self):
        self._logic_worker.init()

    @staticmethod
    def run():
        logger.info('Running event loop')
        webview.start(user_agent=config.USER_AGENT)
        logger.info('Start to shut down')

    def start_shut_down(self):
        self._browser_window.events.loaded -= self._on_browser_loaded
        self._browser_window.events.closing -= self._on_browser_closing
        self._browser_window.destroy()

    def shut_down(self):
        self._logic_worker.start_shut_down()
        self._logic_worker.join(10)

    @property
    def is_standalone_mode(self):
        """不作为blivechat插件运行，而是单独运行"""
        return self._is_standalone_mode

    def set_standalone_mode(self):
        self._is_standalone_mode = True

    def open_admin_ui(self):
        self._browser_window.clear_cookies()
        # 如果不换个URL，不会发loaded事件，会一直等待...
        url = f'https://passport.bilibili.com/login?t={time.time()}'
        self._browser_window.load_url(url)
        self._browser_window.show()

    def _on_browser_closing(self):
        if self.is_standalone_mode:
            return True

        # 插件模式时随主程序一起结束，先不关闭窗口
        self._browser_window.hide()
        self._browser_window.load_html('')
        return False

    def _on_browser_loaded(self):
        simple_cookies: List[http.cookies.SimpleCookie] = self._browser_window.get_cookies()
        async def try_save():
            cookie_jar = aiohttp.CookieJar()
            for simple_cookie in simple_cookies:
                cookie_jar.update_cookies(simple_cookie)

            if not await cookies_mgr.validate_and_save_cookies(cookie_jar):
                return

            if self.is_standalone_mode:
                self.start_shut_down()
            else:
                self._browser_window.hide()
                self._browser_window.load_html('')

        self._logic_worker.run_coro(try_save())


class LogicWorker:
    def __init__(self):
        self._worker_thread = threading.Thread(
            target=asyncio.run, args=(self._worker_thread_func(),), daemon=True
        )
        self._thread_init_future = concurrent.futures.Future()

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._shut_down_event: Optional[asyncio.Event] = None

    def init(self):
        self._worker_thread.start()
        self._thread_init_future.result(10)

    def start_shut_down(self):
        if self._shut_down_event is not None:
            self._loop.call_soon_threadsafe(self._shut_down_event.set)

    def join(self, timeout=None):
        self._worker_thread.join(timeout)
        return not self._worker_thread.is_alive()

    async def _worker_thread_func(self):
        self._loop = asyncio.get_running_loop()
        self._shut_down_event = asyncio.Event()
        try:
            try:
                await self._init_in_worker_thread()
                self._thread_init_future.set_result(None)
            except BaseException as e:
                self._thread_init_future.set_exception(e)
                return

            await self._run()
        finally:
            await self._shut_down()

    @staticmethod
    async def _init_in_worker_thread():
        try:
            await blcsdk.init()
        except blcsdk.InitError as e:
            logger.info('SDK initializing failed: %s', e)
            logger.info('Switch to standalone mode')
            get_app().set_standalone_mode()
        else:
            await listener.init()

        cookies_mgr.init()

    async def _run(self):
        logger.info('Running logic thread event loop')
        await self._shut_down_event.wait()
        logger.info('Logic thread start to shut down')

    @staticmethod
    async def _shut_down():
        await cookies_mgr.shut_down()

        if not get_app().is_standalone_mode:
            listener.shut_down()
            await blcsdk.shut_down()

    # def call_soon(self, func, *args):
    #     self._loop.call_soon_threadsafe(func, *args)

    def run_coro(self, coro: Coroutine):
        self._loop.call_soon_threadsafe(self._loop.create_task, coro)
