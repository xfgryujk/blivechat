# -*- coding: utf-8 -*-
import asyncio
import logging
import os
import re
from typing import *

import aiohttp

from . import (
    __version__,
    client as cli,
    exc,
    handlers,
    models,
)

__all__ = (
    'init',
    'shut_down',
    'set_msg_handler',
    'is_sdk_version_compatible',
)

logger = logging.getLogger('blcsdk')

# 环境变量
_base_url = ''
"""HTTP API的URL"""
_token = ''
"""插件认证用的token"""

# 初始化消息
_init_future: Optional[asyncio.Future] = None
"""初始化消息的future"""
_init_msg: Optional[dict] = None
"""初始化消息，包含版本等信息"""

# 其他和blivechat通信用的对象
_http_session: Optional[aiohttp.ClientSession] = None
"""插件请求专用的HTTP客户端"""
_plugin_client: Optional[cli.BlcPluginClient] = None
"""插件客户端"""
_msg_handler: Optional[handlers.HandlerInterface] = None
"""插件消息处理器"""
_msg_handler_wrapper: Optional['_HandlerWrapper'] = None
"""用于SDK处理一些消息，然后转发给插件消息处理器"""


async def init():
    """
    初始化SDK

    在调用除了set_msg_handler以外的其他接口之前必须先调用这个。如果抛出任何异常，应该退出当前程序
    """
    try:
        global _base_url, _token, _init_future, _init_msg, _http_session, _plugin_client, _msg_handler_wrapper
        if _init_future is not None:
            raise exc.InitError('Cannot call init() again')
        _init_future = asyncio.get_running_loop().create_future()

        # 初始化环境变量信息
        blc_port = int(os.environ['BLC_PORT'])
        _base_url = f'http://localhost:{blc_port}'
        blc_ws_url = f'ws://localhost:{blc_port}/api/plugin/websocket'
        _token = os.environ['BLC_TOKEN']

        _http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers={'Authorization': f'Bearer {_token}'},
        )

        # 连接blivechat
        _msg_handler_wrapper = _HandlerWrapper()
        _plugin_client = cli.BlcPluginClient(blc_ws_url, session=_http_session)
        _plugin_client.set_handler(_msg_handler_wrapper)
        _plugin_client.start()

        # 等待初始化消息
        _init_msg = await _init_future
        logger.debug('SDK initialized, _init_msg=%s', _init_msg)
    except exc.InitError:
        raise
    except Exception as e:
        raise exc.InitError(f'Error in init(): {e}') from e


async def shut_down():
    """退出程序之前建议调用"""
    if _plugin_client is not None:
        await _plugin_client.stop_and_close()
    if _http_session is not None:
        await _http_session.close()


def set_msg_handler(handler: Optional[handlers.HandlerInterface]):
    """
    设置消息处理器

    注意消息处理器和网络协程运行在同一个协程，如果处理消息耗时太长会阻塞接收消息。如果是CPU密集型的任务，建议将消息推到线程池处理；
    如果是IO密集型的任务，应该使用async函数，并且在handler里使用create_task创建新的协程

    :param handler: 消息处理器
    """
    global _msg_handler
    _msg_handler = handler


class _HandlerWrapper(handlers.HandlerInterface):
    """用于SDK处理一些消息，然后转发给插件消息处理器"""

    def handle(self, client: cli.BlcPluginClient, command: dict):
        if not _init_future.done():
            if command['cmd'] == models.Command.BLC_INIT:
                _init_future.set_result(command['data'])

        if _msg_handler is not None:
            _msg_handler.handle(client, command)

    def on_client_stopped(self, client: cli.BlcPluginClient, exception: Optional[Exception]):
        if not _init_future.done():
            if exception is not None:
                _init_future.set_exception(exception)
            else:
                _init_future.set_exception(exc.InitError('Connection closed before init msg'))

        if _msg_handler is not None:
            _msg_handler.on_client_stopped(client, exception)


def is_sdk_version_compatible():
    """
    检查SDK版本和blivechat的版本是否兼容

    如果不兼容，建议退出当前程序。如果继续执行有可能不能正常工作
    """
    if _init_msg is None:
        raise exc.SdkError('Please call init() first')

    major_ver_pattern = r'(\d+)\.\d+\.\d+'
    remote_ver = _init_msg['sdkVersion']

    m = re.match(major_ver_pattern, remote_ver)
    if m is None:
        raise exc.SdkError(f"Bad remote version format: {remote_ver}")
    remote_major_ver = m[1]

    m = re.match(major_ver_pattern, __version__)
    if m is None:
        raise exc.SdkError(f"Bad local version format: {__version__}")
    local_major_ver = m[1]

    res = remote_major_ver == local_major_ver
    if not res:
        logger.warning('SDK version is not compatible, remote=%s, local=%s', remote_ver, __version__)
    return res
