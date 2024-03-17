# -*- coding: utf-8 -*-
import asyncio
import dataclasses
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
    'get_blc_port',
    'get_blc_version',
    'get_blc_sdk_version',
    'get_plugin_id',
    'log',
    'send_text',
    'get_rooms',
)

logger = logging.getLogger('blcsdk')

# 环境变量
_blc_port = 0
"""服务器端口"""
_blc_base_url = ''
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
        global _blc_port, _blc_base_url, _token, _init_future, _init_msg, _http_session, _plugin_client, \
            _msg_handler_wrapper
        if _init_future is not None:
            raise exc.InitError('Cannot call init() again')
        _init_future = asyncio.get_running_loop().create_future()

        # 初始化环境变量信息
        _blc_port = int(os.environ['BLC_PORT'])
        _blc_base_url = f'http://localhost:{_blc_port}'
        blc_ws_url = f'ws://localhost:{_blc_port}/api/plugin/websocket'
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
    assert _init_msg is not None, 'Please call init() first'

    version_pattern = r'(\d+)\.(\d+)\.\d+'
    remote_ver = get_blc_sdk_version()

    m = re.match(version_pattern, remote_ver)
    if m is None:
        raise exc.SdkError(f"Bad remote version format: {remote_ver}")
    remote_major_ver = m[1]
    remote_minor_ver = m[2]

    m = re.match(version_pattern, __version__)
    if m is None:
        raise exc.SdkError(f"Bad local version format: {__version__}")
    local_major_ver = m[1]
    local_minor_ver = m[2]

    res = (
        remote_major_ver == local_major_ver
        and int(remote_minor_ver) >= int(local_minor_ver)
    )
    if not res:
        logger.warning('SDK version is not compatible, remote=%s, local=%s', remote_ver, __version__)
    return res


def get_blc_port():
    """取blivechat服务器监听的端口"""
    assert _blc_port != 0, 'Please call init() first'
    return _blc_port


def get_blc_version() -> str:
    """取blivechat版本"""
    assert _init_msg is not None, 'Please call init() first'
    return _init_msg['blcVersion']


def get_blc_sdk_version() -> str:
    """取blivechat用的SDK版本。是主进程用的版本，不是这个包的__version__"""
    assert _init_msg is not None, 'Please call init() first'
    return _init_msg['sdkVersion']


def get_plugin_id() -> str:
    """取当前插件的ID"""
    assert _init_msg is not None, 'Please call init() first'
    return _init_msg['pluginId']


async def _blc_ws_send_cmd_data(cmd: models.Command, data: dict):
    assert _plugin_client is not None, 'Please call init() first'

    try:
        await _plugin_client.send_cmd_data(cmd, data)
    except (ConnectionResetError, aiohttp.ClientError) as e:
        raise exc.TransportError(str(e)) from e


def _blc_get(rel_url, *, params=None):
    return _blc_http_request('GET', rel_url, params=params)


def _blc_post(rel_url, *, params=None, json=None):
    return _blc_http_request('POST', rel_url, params=params, json=json)


async def _blc_http_request(method, rel_url, **kwargs):
    assert _http_session is not None, 'Please call init() first'

    try:
        async with _http_session.request(method, _blc_base_url + rel_url, **kwargs) as r:
            if r.ok:
                return await r.json()

            try:
                data = await r.json()
            except aiohttp.ContentTypeError:
                data = None
            raise exc.ResponseError(r.status, r.reason, data)
    except aiohttp.ClientError as e:
        raise exc.TransportError(str(e)) from e


async def log(msg, level=logging.INFO):
    """
    输出日志到blivechat

    blivechat不会分离插件的控制台，所以直接输出到标准输出流、标准错误流也能看到日志，但是通过这个接口输出的还会写到blivechat的日志文件
    """
    await _blc_ws_send_cmd_data(models.Command.LOG_REQ, {
        'msg': str(msg),
        'level': level,
    })


async def send_text(
    content: str,
    author_name: str = '',
    *,
    uid: str = '',
    avatar_url: str = '',
    author_type: int = models.AuthorType.NORMAL.value,
    guard_level: int = models.GuardLevel.NONE.value,
    medal_level: int = 0,
    translation: str = '',
    room_key: Optional[models.RoomKey] = None,
):
    """
    发送文字消息

    当前插件也会收到这条消息，注意避免死循环

    :param content: 内容
    :param author_name: 用户名，默认为当前插件ID
    :param uid: 用户Open ID或ID
    :param avatar_url: 用户头像URL，默认自动生成
    :param author_type: 用户类型，见AuthorType
    :param guard_level: 舰队等级，见GuardLevel
    :param medal_level: 勋章等级
    :param translation: 内容翻译
    :param room_key: 发送到哪个房间，默认发送到所有房间
    """
    await _blc_ws_send_cmd_data(models.Command.ADD_TEXT_REQ, {
        'content': content,
        'authorName': author_name,
        'uid': uid,
        'avatarUrl': avatar_url,
        'authorType': author_type,
        'guardLevel': guard_level,
        'medalLevel': medal_level,
        'translation': translation,
        'roomKey': room_key.to_dict() if room_key is not None else None,
    })


@dataclasses.dataclass
class GetRoomsRes:
    room_id: Optional[int]
    """房间ID，初始化之前是None"""
    room_key: models.RoomKey
    """blivechat用来标识一个房间的key"""


async def get_rooms() -> List[GetRoomsRes]:
    """取当前已创建的房间列表"""
    rsp = await _blc_get('/api/plugin/rooms')
    rooms = [
        GetRoomsRes(
            room_id=room_dict['roomId'],
            room_key=models.RoomKey.from_dict(room_dict['roomKey']),
        )
        for room_dict in rsp['rooms']
    ]
    return rooms
