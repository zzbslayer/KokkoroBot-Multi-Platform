import re
import json
import os
from typing import Callable, Dict
from kokkoro import logger, log, typing

# service management
_loaded_services: Dict[str, "Service"] = {}  # {name: service}
_re_illegal_char = re.compile(r'[\\/:*?"<>|\.]')
_service_config_dir = os.path.expanduser('~/.hoshino/service_config/')
os.makedirs(_service_config_dir, exist_ok=True)

def _load_service_config(service_name):
    config_file = os.path.join(_service_config_dir, f'{service_name}.json')
    if not os.path.exists(config_file):
        return {}  # config file not found, return default config.
    try:
        with open(config_file, encoding='utf8') as f:
            config = json.load(f)
            return config
    except Exception as e:
        logger.exception(e)
        return {}


def _save_service_config(service):
    config_file = os.path.join(_service_config_dir, f'{service.name}.json')
    with open(config_file, 'w', encoding='utf8') as f:
        json.dump(
            {
                "name": service.name,
                "use_priv": service.use_priv,
                "manage_priv": service.manage_priv,
                "enable_on_default": service.enable_on_default,
                "visible": service.visible,
                "enable_group": list(service.enable_group),
                "disable_group": list(service.disable_group)
            },
            f,
            ensure_ascii=False,
            indent=2)

class ServiceFunc:
    def __init__(self, sv: "Service", func: Callable, only_to_me: bool):
        self.sv = sv
        self.func = func
        self.only_to_me = only_to_me
        self.__name__ = func.__name__

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class Service:
    """将一组功能包装为服务, 提供增强的触发条件与分群权限管理.

    支持的触发条件:
    `on_message`,
    `on_prefix`, `on_fullmatch`, `on_suffix`,
    `on_keyword`, `on_rex`,
    `on_command`, `on_natural_language`

    提供接口：
    `scheduled_job`, `broadcast`

    服务的配置文件格式为：
    {
        "name": "ServiceName",
        "use_priv": priv.NORMAL,
        "manage_priv": priv.ADMIN,
        "enable_on_default": true/false,
        "visible": true/false,
        "enable_group": [],
        "disable_group": []
    }

    储存位置：
    `~/.kokkoro/service_config/{ServiceName}.json`
    """
    def __init__(self, name, use_priv=None, manage_priv=None, enable_on_default=None, visible=None,
                 help_=None):
        """
        定义一个服务
        配置的优先级别：配置文件 > 程序指定 > 缺省值
        """
        #assert not _re_illegal_char.search(name), r'Service name cannot contain character in `\/:*?"<>|.`'

        config = _load_service_config(name)
        self.name = name
        #self.use_priv = config.get('use_priv') or use_priv or priv.NORMAL
        #self.manage_priv = config.get('manage_priv') or manage_priv or priv.ADMIN
        self.enable_on_default = config.get('enable_on_default')
        if self.enable_on_default is None:
            self.enable_on_default = enable_on_default
        if self.enable_on_default is None:
            self.enable_on_default = True
        self.visible = config.get('visible')
        if self.visible is None:
            self.visible = visible
        if self.visible is None:
            self.visible = True
        self.help = help_
        self.enable_group = set(config.get('enable_group', []))
        self.disable_group = set(config.get('disable_group', []))

        self.logger = log.new_logger(name)

        assert self.name not in _loaded_services, f'Service name "{self.name}" already exist!'
        _loaded_services[self.name] = self
