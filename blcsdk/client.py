# -*- coding: utf-8 -*-
import asyncio
import logging
from typing import *

import aiohttp

from . import handlers
from . import models

__all__ = (
    'BlcPluginClient',
)

logger = logging.getLogger('blcsdk')


class BlcPluginClient:
    """
    blivechat插件服务的客户端

    :param ws_url: blivechat消息转发服务WebSocket地址
    :param session: 连接池
    :param heartbeat_interval: 发送心跳包的间隔时间（秒）
    """

    def __init__(
        self,
        ws_url: str,
        *,
        session: Optional[aiohttp.ClientSession] = None,
        heartbeat_interval: float = 30,
    ):
        self._ws_url = ws_url

        if session is None:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
            self._own_session = True
        else:
            self._session = session
            self._own_session = False
            assert self._session.loop is asyncio.get_event_loop()  # noqa

        self._heartbeat_interval = heartbeat_interval

        self._handler: Optional[handlers.HandlerInterface] = None
        """消息处理器"""

        # 在运行时初始化的字段
        self._websocket: Optional[aiohttp.ClientWebSocketResponse] = None
        """WebSocket连接"""
        self._network_future: Optional[asyncio.Future] = None
        """网络协程的future"""
        self._heartbeat_timer_handle: Optional[asyncio.TimerHandle] = None
        """发心跳包定时器的handle"""

    @property
    def is_running(self) -> bool:
        """本客户端正在运行，注意调用stop后还没完全停止也算正在运行"""
        return self._network_future is not None

    def set_handler(self, handler: Optional['handlers.HandlerInterface']):
        """
        设置消息处理器

        注意消息处理器和网络协程运行在同一个协程，如果处理消息耗时太长会阻塞接收消息。如果是CPU密集型的任务，建议将消息推到线程池处理；
        如果是IO密集型的任务，应该使用async函数，并且在handler里使用create_task创建新的协程

        :param handler: 消息处理器
        """
        self._handler = handler

    def start(self):
        """启动本客户端"""
        if self.is_running:
            logger.warning('Plugin client is running, cannot start() again')
            return

        self._network_future = asyncio.create_task(self._network_coroutine_wrapper())

    def stop(self):
        """停止本客户端"""
        if not self.is_running:
            logger.warning('Plugin client is stopped, cannot stop() again')
            return

        self._network_future.cancel()

    async def stop_and_close(self):
        """便利函数，停止本客户端并释放本客户端的资源，调用后本客户端将不可用"""
        if self.is_running:
            self.stop()
            await self.join()
        await self.close()

    async def join(self):
        """等待本客户端停止"""
        if not self.is_running:
            logger.warning('Plugin client is stopped, cannot join()')
            return

        await asyncio.shield(self._network_future)

    async def close(self):
        """释放本客户端的资源，调用后本客户端将不可用"""
        if self.is_running:
            logger.warning('Plugin is calling close(), but client is running')

        # 如果session是自己创建的则关闭session
        if self._own_session:
            await self._session.close()

    async def send_cmd_data(self, cmd: models.Command, data: dict):
        """
        发送消息给服务器

        :param cmd: 消息类型，见Command
        :param data: 消息体JSON数据
        """
        if self._websocket is None or self._websocket.closed:
            raise ConnectionResetError('websocket is closed')

        body = {'cmd': cmd, 'data': data}
        await self._websocket.send_json(body)

    async def _network_coroutine_wrapper(self):
        """负责处理网络协程的异常，网络协程具体逻辑在_network_coroutine里"""
        exc = None
        try:
            await self._network_coroutine()
        except asyncio.CancelledError:
            # 正常停止
            pass
        except Exception as e:
            logger.exception('_network_coroutine() finished with exception:')
            exc = e
        finally:
            logger.debug('_network_coroutine() finished')
            self._network_future = None

        if self._handler is not None:
            self._handler.on_client_stopped(self, exc)

    async def _network_coroutine(self):
        """网络协程，负责连接服务器、接收消息、解包"""
        try:
            # 连接
            async with self._session.ws_connect(
                self._ws_url,
                receive_timeout=self._heartbeat_interval + 5,
            ) as websocket:
                self._websocket = websocket
                await self._on_ws_connect()

                # 处理消息
                message: aiohttp.WSMessage
                async for message in websocket:
                    self._on_ws_message(message)
        finally:
            self._websocket = None
            await self._on_ws_close()
        # 插件消息都是本地通信的，这里不可能是因为网络问题而掉线，所以不尝试重连

    async def _on_ws_connect(self):
        """WebSocket连接成功"""
        self._heartbeat_timer_handle = asyncio.get_running_loop().call_later(
            self._heartbeat_interval, self._on_send_heartbeat
        )

    async def _on_ws_close(self):
        """WebSocket连接断开"""
        if self._heartbeat_timer_handle is not None:
            self._heartbeat_timer_handle.cancel()
            self._heartbeat_timer_handle = None

    def _on_send_heartbeat(self):
        """定时发送心跳包的回调"""
        if self._websocket is None or self._websocket.closed:
            self._heartbeat_timer_handle = None
            return

        self._heartbeat_timer_handle = asyncio.get_running_loop().call_later(
            self._heartbeat_interval, self._on_send_heartbeat
        )
        asyncio.create_task(self._send_heartbeat())

    async def _send_heartbeat(self):
        """发送心跳包"""
        try:
            await self.send_cmd_data(models.Command.HEARTBEAT, {})
        except (ConnectionResetError, aiohttp.ClientConnectionError) as e:
            logger.warning('Plugin client _send_heartbeat() failed: %r', e)
        except Exception:  # noqa
            logger.exception('Plugin client _send_heartbeat() failed:')

    def _on_ws_message(self, message: aiohttp.WSMessage):
        """
        收到WebSocket消息

        :param message: WebSocket消息
        """
        if message.type != aiohttp.WSMsgType.TEXT:
            logger.warning('Unknown websocket message type=%s, data=%s', message.type, message.data)
            return

        try:
            body = message.json()
            self._handle_command(body)
        except Exception:
            logger.error('body=%s', message.data)
            raise

    def _handle_command(self, command: dict):
        """
        处理业务消息

        :param command: 业务消息
        """
        if self._handler is not None:
            try:
                self._handler.handle(self, command)
            except Exception as e:
                logger.exception('Plugin client _handle_command() failed, command=%s', command, exc_info=e)
