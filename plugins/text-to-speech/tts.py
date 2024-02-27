# -*- coding: utf-8 -*-
import dataclasses
import enum
import logging
import queue
import threading
from typing import *

import pyttsx3.voice

import config

logger = logging.getLogger('text-to-speech.' + __name__)

_tts: Optional['Tts'] = None


class Priority(enum.IntEnum):
    HIGH = 0
    NORMAL = 1


@dataclasses.dataclass
class TtsTask:
    priority: Priority
    text: str


def init():
    global _tts
    _tts = Tts()
    return _tts.init()


def say(text, priority: Priority = Priority.NORMAL):
    logger.debug('%s', text)
    task = TtsTask(priority=priority, text=text)
    res = _tts.push_task(task)
    if not res:
        if task.priority == Priority.HIGH:
            logger.info('Dropped high priority task: %s', task.text)
        else:
            logger.debug('Dropped task: %s', task.text)
    return res


class Tts:
    def __init__(self):
        self._worker_thread = threading.Thread(target=self._worker_thread_func, daemon=True)
        # COM组件必须在使用它的线程里初始化，否则使用时会有问题
        self._engine: Optional[pyttsx3.Engine] = None
        self._thread_init_event = threading.Event()

        cfg = config.get_config()
        self._task_queues: List[queue.Queue['TtsTask']] = [
            queue.Queue(cfg.max_tts_queue_size) for _ in range(len(Priority))
        ]
        """任务队列，索引是优先级"""

    def init(self):
        self._worker_thread.start()
        res = self._thread_init_event.wait(10)
        if not res:
            logger.error('Initializing TTS engine timed out')
        return res

    def _init_in_worker_thread(self):
        logger.info('Initializing TTS engine')
        self._engine = pyttsx3.init()

        voices = cast(List[pyttsx3.voice.Voice], self._engine.getProperty('voices'))
        logger.info('Available voices:\n%s', '\n'.join(map(str, voices)))

        cfg = config.get_config()
        if cfg.tts_voice_id is not None:
            self._engine.setProperty('voice', cfg.tts_voice_id)
        self._engine.setProperty('rate', cfg.tts_rate)
        self._engine.setProperty('volume', cfg.tts_volume)

        self._thread_init_event.set()

    # TODO 自己实现队列，合并礼物消息
    def push_task(self, task: TtsTask):
        q = self._task_queues[task.priority]
        try:
            q.put_nowait(task)
            return True
        except queue.Full:
            pass

        if task.priority != Priority.HIGH:
            return False

        # 高优先级的尝试降级，挤掉低优先级的任务
        q = self._task_queues[Priority.NORMAL]
        while True:
            try:
                q.put_nowait(task)
                break
            except queue.Full:
                try:
                    task = q.get_nowait()
                    if task.priority == Priority.HIGH:
                        logger.info('Dropped high priority task: %s', task.text)
                    else:
                        logger.debug('Dropped task: %s', task.text)
                except queue.Empty:
                    pass
        return True

    def _pop_task(self) -> TtsTask:
        while True:
            # 按优先级遍历，轮询等待任务
            for q in self._task_queues:
                try:
                    return q.get(timeout=0.1)
                except queue.Empty:
                    pass

    def _worker_thread_func(self):
        self._init_in_worker_thread()

        logger.info('Running TTS worker')
        while True:
            task = self._pop_task()
            self._engine.say(task.text)
            self._engine.runAndWait()
