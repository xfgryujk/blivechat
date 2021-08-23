# -*- coding: utf-8 -*-

import asyncio
import logging
import threading

import aiohttp
import tornado.ioloop
import tornado.web

import api.chat
import config
import main
import models.avatar
import models.translate
import models.database
import update
import window.main
from window.console import ConsoleHandler


def _server_thread(loop, args_):
    asyncio.set_event_loop(loop)
    main.main(args_)


def override(loop):
    # event loop for thread
    models.avatar._main_event_loop = loop
    models.translate._main_event_loop = loop
    asyncio.ensure_future(api.chat._http_session.close())
    api.chat._http_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10), loop=loop)
    asyncio.ensure_future(models.avatar._http_session.close())
    models.avatar._http_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10), loop=loop)

    # disable web browser when start.
    def _run_server_override(host, port, debug):
        app = tornado.web.Application(
            main.routes,
            websocket_ping_interval=10,
            debug=debug,
            autoreload=False
        )
        cfg = config.get_config()
        try:
            app.listen(
                port,
                host,
                xheaders=cfg.tornado_xheaders
            )
        except OSError:
            main.logger.warning('Address is used %s:%d', host, port)
            return
        finally:
            window.main.config_url = 'http://localhost%s/?_v=%s' % (
                f':{port}' if port != 80 else '',
                update.VERSION  # 防止更新版本后浏览器加载缓存
            )
            window.main.console.button_open_admin.setEnabled(True)
            window.main.console.action_open_admin.setEnabled(True)
            window.main.console.button_float_window.setEnabled(True)
            window.main.console.action_float_window.setEnabled(True)
        main.logger.info('Server started: %s:%d', host, port)
        tornado.ioloop.IOLoop.current().start()

    # add ui handler to logger
    def _init_logging_override(debug):
        # noinspection PyArgumentList
        main.logging.basicConfig(
            format='{asctime} {levelname} [{threadName}] [{name}]: {message}',
            datefmt='%Y-%m-%d %H:%M:%S',
            style='{',
            level=main.logging.INFO if not debug else main.logging.DEBUG,
            handlers=[
                main.logging.StreamHandler(ConsoleHandler()),
                # main.logging.StreamHandler(),
                main.logging.handlers.TimedRotatingFileHandler(
                    main.LOG_FILE_NAME, encoding='utf-8', when='midnight', backupCount=7, delay=True
                )
            ]
        )
        if not debug:
            logging.getLogger('tornado.access').setLevel(logging.WARNING)

    # hook to args parser
    def _main_override(args_):
        main.init_logging(args_.debug)
        config.init()
        models.database.init(args_.debug)
        models.avatar.init()
        models.translate.init()
        api.chat.init()
        update.check_update()

        main.run_server(args_.host, args_.port, args_.debug)

    main.run_server = _run_server_override
    main.init_logging = _init_logging_override
    main.main = _main_override


if __name__ == '__main__':
    args = main.parse_args()
    window.main.init(args)

    server_loop = asyncio.new_event_loop()
    override(server_loop)
    server_thread = threading.Thread(target=_server_thread, args=(server_loop, args), name='thread_server')
    server_thread.setDaemon(True)
    server_thread.start()

    window.main.loop()
