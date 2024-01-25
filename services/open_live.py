# -*- coding: utf-8 -*-
import asyncio
import dataclasses
import datetime
import logging
from typing import *

import api.open_live
import config
import utils.async_io

logger = logging.getLogger(__name__)

# 正在等待发送的心跳任务，game_id -> HeartbeatTask
_game_id_heart_task_map: Dict[str, 'HeartbeatTask'] = {}


@dataclasses.dataclass
class HeartbeatTask:
    game_id: str
    future: 'asyncio.Future[dict]'


def init():
    cfg = config.get_config()
    # 批量心跳只支持配置了开放平台的公共服务器，私有服务器用的人少，意义不大
    if cfg.is_open_live_configured:
        utils.async_io.create_task_with_ref(_game_heartbeat_consumer())


async def send_game_heartbeat(game_id) -> dict:
    """发送项目心跳。成功则返回符合开放平台格式的结果，失败则抛出异常"""
    assert config.get_config().is_open_live_configured
    if game_id in (None, ''):
        raise api.open_live.BusinessError({'code': 4000, 'message': '参数错误', 'request_id': '0', 'data': None})

    task = _game_id_heart_task_map.get(game_id, None)
    if task is None:
        task = HeartbeatTask(
            game_id=game_id,
            future=asyncio.get_running_loop().create_future(),
        )

        _game_id_heart_task_map[game_id] = task
        # 限制一次发送的数量，数量太多了就立即发送
        if len(_game_id_heart_task_map) >= 200:
            await _flush_game_heartbeat_tasks()

    return await task.future


async def _game_heartbeat_consumer():
    while True:
        try:
            start_time = datetime.datetime.now()
            await _flush_game_heartbeat_tasks()
            cost_time = (datetime.datetime.now() - start_time).total_seconds()

            # 如果等待时间太短，请求频率会太高；如果等待时间太长，前端请求、项目心跳会超时
            await asyncio.sleep(4 - cost_time)
        except Exception:  # noqa
            logger.exception('_heartbeat_consumer error:')


async def _flush_game_heartbeat_tasks():
    global _game_id_heart_task_map
    if not _game_id_heart_task_map:
        return
    game_id_task_map = _game_id_heart_task_map
    _game_id_heart_task_map = {}

    game_ids = list(game_id_task_map.keys())
    logger.info('Sending game batch heartbeat for %d games', len(game_ids))
    try:
        res = await api.open_live.request_open_live(
            api.open_live.GAME_BATCH_HEARTBEAT_OPEN_LIVE_URL,
            {'game_ids': game_ids},
            ignore_rate_limit=True
        )
        failed_game_ids = res['data']['failed_game_ids']
        if failed_game_ids is None:  # 哪个SB后端给数组传null的
            failed_game_ids = set()
        else:
            failed_game_ids = set(failed_game_ids)
        request_id = res['request_id']
    except Exception as e:
        for task in game_id_task_map.values():
            task.future.set_exception(e)
        return
    if failed_game_ids:
        logger.info(
            'Game batch heartbeat res: %d succeeded, %d failed, request_id=%s',
            len(game_ids) - len(failed_game_ids), len(failed_game_ids), request_id
        )

    for task in game_id_task_map.values():
        if task.game_id in failed_game_ids:
            task.future.set_exception(api.open_live.BusinessError(
                {'code': 7003, 'message': '心跳过期或GameId错误', 'request_id': request_id, 'data': None}
            ))
        else:
            task.future.set_result({'code': 0, 'message': '0', 'request_id': request_id, 'data': None})
