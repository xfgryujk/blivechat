# -*- coding: utf-8 -*-
__all__ = (
    'SdkError',
    'InitError',
)


class SdkError(Exception):
    """SDK错误的基类"""


class InitError(SdkError):
    """初始化失败"""
