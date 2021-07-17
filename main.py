# -*- coding: utf-8 -*-

import argparse
import logging
import logging.handlers
import os
import webbrowser

import tornado.ioloop
import tornado.web

import api.chat
import api.main
import config
import models.avatar
import models.database
import models.translate
import update

logger = logging.getLogger(__name__)

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
WEB_ROOT = os.path.join(BASE_PATH, 'frontend', 'dist')
LOG_FILE_NAME = os.path.join(BASE_PATH, 'log', 'blivechat.log')

routes = [
    (r'/api/server_info', api.main.ServerInfoHandler),
    (r'/api/chat', api.chat.ChatHandler),
    (r'/api/room_info', api.chat.RoomInfoHandler),
    (r'/api/avatar_url', api.chat.AvatarHandler),

    (r'/(.*)', api.main.MainHandler, {'path': WEB_ROOT, 'default_filename': 'index.html'})
]


def main():
    args = parse_args()

    init_logging(args.debug)
    config.init()
    models.database.init(args.debug)
    models.avatar.init()
    models.translate.init()
    api.chat.init()
    update.check_update()

    run_server(args.host, args.port, args.debug)


def parse_args():
    parser = argparse.ArgumentParser(description='用于OBS的仿YouTube风格的bilibili直播评论栏')
    parser.add_argument('--host', help='服务器host，默认为127.0.0.1', default='127.0.0.1')
    parser.add_argument('--port', help='服务器端口，默认为12450', type=int, default=12450)
    parser.add_argument('--debug', help='调试模式', action='store_true')
    return parser.parse_args()


def init_logging(debug):
    stream_handler = logging.StreamHandler()
    file_handler = logging.handlers.TimedRotatingFileHandler(
        LOG_FILE_NAME, encoding='utf-8', when='midnight', backupCount=7, delay=True
    )
    # noinspection PyArgumentList
    logging.basicConfig(
        format='{asctime} {levelname} [{name}]: {message}',
        datefmt='%Y-%m-%d %H:%M:%S',
        style='{',
        level=logging.INFO if not debug else logging.DEBUG,
        handlers=[stream_handler, file_handler]
    )

    # 屏蔽访问日志
    logging.getLogger('tornado.access').setLevel(logging.WARNING)


def run_server(host, port, debug):
    app = tornado.web.Application(
        routes,
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
        logger.warning('Address is used %s:%d', host, port)
        return
    finally:
        url = 'http://localhost/' if port == 80 else f'http://localhost:{port}/'
        # 防止更新版本后浏览器加载缓存
        url += '?_v=' + update.VERSION
        webbrowser.open(url)
    logger.info('Server started: %s:%d', host, port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
