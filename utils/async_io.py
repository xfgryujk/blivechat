# -*- coding: utf-8 -*-
import asyncio

# 只用于持有Task的引用
_task_refs = set()


def create_task_with_ref(*args, **kwargs):
    """创建Task并保持引用，防止协程执行完之前就被GC"""
    task = asyncio.create_task(*args, **kwargs)
    _task_refs.add(task)
    task.add_done_callback(_task_refs.discard)
    return task
