# -*- coding: utf-8 -*-
import dataclasses
import datetime
import json
import logging
import os
import random
import string
import subprocess
from typing import *

import api.plugin
import blcsdk
import blcsdk.models as sdk_models
import config
import update

logger = logging.getLogger(__name__)

PLUGINS_PATH = os.path.join(config.DATA_PATH, 'plugins')

_plugins: Dict[str, 'Plugin'] = {}


def init():
    plugin_ids = _discover_plugin_ids()
    if not plugin_ids:
        return
    logger.info('Found plugins: %s', plugin_ids)

    for plugin_id in plugin_ids:
        plugin = _create_plugin(plugin_id)
        if plugin is not None:
            _plugins[plugin_id] = plugin

    for plugin in _plugins.values():
        if plugin.enabled:
            try:
                plugin.start()
            except StartPluginError:
                pass


def shut_down():
    for plugin in _plugins.values():
        plugin.stop()


def _discover_plugin_ids():
    res = []
    try:
        with os.scandir(PLUGINS_PATH) as it:
            for entry in it:
                if entry.is_dir() and os.path.isfile(os.path.join(entry.path, 'plugin.json')):
                    res.append(entry.name)
    except OSError:
        logger.exception('Failed to discover plugins:')
    return res


def _create_plugin(plugin_id):
    config_path = os.path.join(PLUGINS_PATH, plugin_id, 'plugin.json')
    try:
        plugin_config = PluginConfig.from_file(config_path)
    except (OSError, json.JSONDecodeError, TypeError):
        logger.exception('plugin=%s failed to load config:', plugin_id)
        return None
    return Plugin(plugin_id, plugin_config)


def iter_plugins() -> Iterable['Plugin']:
    return _plugins.values()


def get_plugin(plugin_id):
    return _plugins.get(plugin_id, None)


def get_plugin_by_token(token):
    if token == '':
        return None
    # 应该最多就十几个插件吧，偷懒用遍历了
    for plugin in _plugins.values():
        if plugin.token == token:
            return plugin
    return None


def broadcast_cmd_data(cmd, data, extra: Optional[dict] = None):
    body = api.plugin.make_message_body(cmd, data, extra)
    for plugin in _plugins.values():
        plugin.send_body_no_raise(body)


@dataclasses.dataclass
class PluginConfig:
    name: str = ''
    version: str = ''
    author: str = ''
    description: str = ''
    run_cmd: str = ''
    enabled: bool = False

    @classmethod
    def from_file(cls, path):
        with open(path, encoding='utf-8') as f:
            cfg = json.load(f)
        if not isinstance(cfg, dict):
            raise TypeError(f'Config type error, type={type(cfg)}')

        return cls(
            name=str(cfg.get('name', '')),
            version=str(cfg.get('version', '')),
            author=str(cfg.get('author', '')),
            description=str(cfg.get('description', '')),
            run_cmd=str(cfg.get('run', '')),
            enabled=bool(cfg.get('enabled', False)),
        )

    def save(self, path):
        try:
            with open(path, encoding='utf-8') as f:
                cfg = json.load(f)
            if not isinstance(cfg, dict):
                raise TypeError(f'Config type error, type={type(cfg)}')
        except (OSError, json.JSONDecodeError, TypeError):
            cfg = {}

        cfg['name'] = self.name
        cfg['version'] = self.version
        cfg['author'] = self.author
        cfg['description'] = self.description
        cfg['run_cmd'] = self.run_cmd
        cfg['enabled'] = self.enabled

        tmp_path = path + '.tmp'
        with open(tmp_path, encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)


class StartPluginError(Exception):
    """启动插件时错误"""


class StartTooFrequently(StartPluginError):
    """启动插件太频繁"""


class Plugin:
    def __init__(self, plugin_id, cfg: PluginConfig):
        self._id = plugin_id
        self._config = cfg

        self._last_start_time = datetime.datetime.fromtimestamp(0)
        self._token = ''
        self._client: Optional['api.plugin.PluginWsHandler'] = None

    @property
    def id(self):
        return self._id

    @property
    def config(self):
        return self._config

    @property
    def enabled(self):
        return self._config.enabled

    @enabled.setter
    def enabled(self, value):
        if self._config.enabled == value:
            return
        self._config.enabled = value

        config_path = os.path.join(self.base_path, 'plugin.json')
        try:
            self._config.save(config_path)
        except OSError:
            logger.exception('plugin=%s failed to save config', self._id)

        if value:
            self.start()
        else:
            self.stop()

    @property
    def base_path(self):
        return os.path.join(PLUGINS_PATH, self._id)

    @property
    def token(self):
        return self._token

    @property
    def is_started(self):
        return self._token != ''

    @property
    def is_connected(self):
        return self._client is not None

    def start(self):
        if self.is_started:
            return

        cur_time = datetime.datetime.now()
        if cur_time - self._last_start_time < datetime.timedelta(seconds=3):
            raise StartTooFrequently(f'plugin={self._id} starts too frequently')
        self._last_start_time = cur_time

        token = ''.join(random.choice(string.hexdigits) for _ in range(32))
        self._set_token(token)

        cfg = config.get_config()
        env = {
            **os.environ,
            'BLC_PORT': str(cfg.port),
            'BLC_TOKEN': self._token,
        }
        try:
            subprocess.Popen(
                self._config.run_cmd,
                shell=True,
                cwd=self.base_path,
                env=env,
            )
        except OSError as e:
            logger.exception('plugin=%s failed to start', self._id)
            raise StartPluginError(str(e))

    def stop(self):
        if self.is_started:
            self._set_token('')

    def _set_token(self, token):
        if self._token == token:
            return
        self._token = token

        # 踢掉已经连接的客户端
        self._set_client(None)

    def _set_client(self, client: Optional['api.plugin.PluginWsHandler']):
        if self._client is client:
            return
        if self._client is not None:
            logger.info('plugin=%s closing old client', self._id)
            self._client.close()
        self._client = client

    def on_client_connect(self, client: 'api.plugin.PluginWsHandler'):
        self._set_client(client)

        # 发送初始化消息
        self.send_cmd_data(sdk_models.Command.BLC_INIT, {
            'blcVersion': update.VERSION,
            'sdkVersion': blcsdk.__version__,
            'pluginId': self._id,
        })

    def on_client_close(self, client: 'api.plugin.PluginWsHandler'):
        if self._client is client:
            self._set_client(None)

    def send_cmd_data(self, cmd, data, extra: Optional[dict] = None):
        if self._client is not None:
            self._client.send_cmd_data(cmd, data, extra)

    def send_body_no_raise(self, body):
        if self._client is not None:
            self._client.send_body_no_raise(body)
