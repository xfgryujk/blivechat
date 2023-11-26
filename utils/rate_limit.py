# -*- coding: utf-8 -*-
import datetime
import logging

logger = logging.getLogger(__name__)


class TokenBucket:
    def __init__(self, tokens_per_sec, max_token_num):
        self._tokens_per_sec = float(tokens_per_sec)
        self._max_token_num = float(max_token_num)
        self._stored_token_num = self._max_token_num
        self._last_update_time = datetime.datetime.now()

        if self._tokens_per_sec <= 0.0 and self._max_token_num >= 1.0:
            logger.warning('TokenBucket token_per_sec=%f <= 0, rate has no limit', tokens_per_sec)

    def try_decrease_token(self):
        if self._tokens_per_sec <= 0.0:
            # self._max_token_num < 1.0 时完全禁止
            return self._max_token_num >= 1.0

        cur_time = datetime.datetime.now()
        last_update_time = min(self._last_update_time, cur_time)  # 防止时钟回拨
        add_token_num = (cur_time - last_update_time).total_seconds() * self._tokens_per_sec
        self._stored_token_num = min(self._stored_token_num + add_token_num, self._max_token_num)
        self._last_update_time = cur_time

        if self._stored_token_num < 1.0:
            return False
        self._stored_token_num -= 1.0
        return True
