# -*- coding: utf-8 -*-
from typing import *

__all__ = (
    'SdkError',
    'InitError',
    'TransportError',
    'ResponseError',
)


class SdkError(Exception):
    """SDK错误的基类"""


class InitError(SdkError):
    """初始化失败"""


class TransportError(SdkError):
    """通信错误"""


class ResponseError(SdkError):
    """响应代码错误"""
    def __init__(self, code: int, msg: str, data: Optional[dict] = None):
        super().__init__(f'code={code}, msg={msg}, data={data}')
        self.code = code
        self.msg = msg
        self.data = data
