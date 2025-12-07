#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging.handlers
import os
import signal
import sys

import app
import config

logger = logging.getLogger('login')


def main():
    try:
        init()
        run()
    finally:
        shut_down()
    return 0


def init():
    init_signal_handlers()

    init_logging()

    app.init()


def init_signal_handlers():
    for signum in (signal.SIGINT, signal.SIGTERM):
        signal.signal(signum, start_shut_down)


def start_shut_down(*_args):
    app_ = app.get_app()
    if app_ is not None:
        app_.start_shut_down()


def init_logging():
    filename = os.path.join(config.LOG_PATH, 'login.log')
    stream_handler = logging.StreamHandler()
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename, encoding='utf-8', when='midnight', backupCount=7, delay=True
    )
    logging.basicConfig(
        format='{asctime} {levelname} [{name}]: {message}',
        style='{',
        level=logging.INFO,
        # level=logging.DEBUG,
        handlers=[stream_handler, file_handler],
    )


def run():
    app.get_app().run()


def shut_down():
    app_ = app.get_app()
    if app_ is not None:
        app_.shut_down()


if __name__ == '__main__':
    sys.exit(main())
