# -*- coding: utf-8 -*-
import collections
import dataclasses
import enum
import logging
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

    @property
    def tts_text(self):
        raise NotImplementedError

    def merge(self, task: 'TtsTask'):
        return False


@dataclasses.dataclass
class TextTtsTask(TtsTask):
    text: str

    @property
    def tts_text(self):
        return self.text


@dataclasses.dataclass
class GiftTtsTask(TtsTask):
    author_name: str
    num: int
    gift_name: str
    price: float
    total_coin: int

    @property
    def tts_text(self):
        cfg = config.get_config()
        is_paid_gift = self.price > 0.
        template = cfg.template_paid_gift if is_paid_gift else cfg.template_free_gift
        text = template.format(
            author_name=self.author_name,
            num=self.num,
            gift_name=self.gift_name,
            price=self.price,
            total_coin=self.total_coin,
        )
        return text

    def merge(self, task: 'TtsTask'):
        if not isinstance(task, GiftTtsTask):
            return False
        if task.author_name != self.author_name or task.gift_name != self.gift_name:
            return False
        self.num += task.num
        self.price += task.price
        self.total_coin += task.total_coin
        return True


def init():
    global _tts
    _tts = Tts()
    return _tts.init()


def say_text(text, priority: Priority = Priority.NORMAL):
    task = TextTtsTask(priority=priority, text=text)
    return say(task)


def say(task: TtsTask):
    logger.debug('%s', task.tts_text)
    res = _tts.push_task(task)
    if not res:
        if task.priority == Priority.HIGH:
            logger.info('Dropped high priority task: %s', task.tts_text)
        else:
            logger.debug('Dropped task: %s', task.tts_text)
    return res


class Tts:
    def __init__(self):
        self._worker_thread = threading.Thread(target=self._worker_thread_func, daemon=True)
        # COM组件必须在使用它的线程里初始化，否则使用时会有问题
        self._engine: Optional[pyttsx3.Engine] = None
        self._thread_init_event = threading.Event()

        cfg = config.get_config()
        self._task_queues = TaskQueue(cfg.max_tts_queue_size)

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
        if cfg.tts_voice_id != '':
            self._engine.setProperty('voice', cfg.tts_voice_id)
        self._engine.setProperty('rate', cfg.tts_rate)
        self._engine.setProperty('volume', cfg.tts_volume)

        self._thread_init_event.set()

    def push_task(self, task: TtsTask):
        return self._task_queues.push(task)

    def _worker_thread_func(self):
        self._init_in_worker_thread()

        logger.info('Running TTS worker')
        while True:
            task = self._task_queues.pop()
            self._engine.say(task.tts_text)
            self._engine.runAndWait()


class TaskQueue:
    def __init__(self, max_size=None):
        self._max_size: Optional[int] = max_size
        self._queues: List[collections.deque[TtsTask]] = [
            collections.deque(maxlen=self._max_size) for _ in Priority
        ]
        """任务队列，索引是优先级"""
        self._lock = threading.Lock()
        self._not_empty_condition = threading.Condition(self._lock)

    def push(self, task: TtsTask):
        with self._lock:
            q = self._queues[task.priority]

            # 尝试合并
            try_merge_count = 0
            for old_task in reversed(q):
                if old_task.merge(task):
                    return True

                try_merge_count += 1
                if try_merge_count >= 5:
                    break

            # 没满直接push
            if (
                self._max_size is None
                or sum(len(q_) for q_ in self._queues) < self._max_size
            ):
                q.append(task)
                self._not_empty_condition.notify()
                return True

            if task.priority != Priority.HIGH:
                return False

            # 高优先级的尝试挤掉低优先级的任务
            lower_q = self._queues[Priority.NORMAL]
            try:
                old_task = lower_q.popleft()
            except IndexError:
                return False
            logger.debug('Dropped task: %s', old_task.tts_text)

            q.append(task)
            self._not_empty_condition.notify()
            return True

    def pop(self) -> TtsTask:
        with self._lock:
            while True:
                # 按优先级遍历查找任务
                for q in self._queues:
                    try:
                        return q.popleft()
                    except IndexError:
                        pass

                self._not_empty_condition.wait()
